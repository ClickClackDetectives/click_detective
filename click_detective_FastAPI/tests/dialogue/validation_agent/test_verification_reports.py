"""검증 책임 분리 후에도 배치·보고서 재요청·의미상 거절 정책을 유지한다."""

import json

import pytest
import pytest_asyncio
from fastapi import HTTPException

from app.dialogue.interrogation_graph import InterrogationGraph
from app.main import create_app
from tests.conftest import redact

from ..models import ApprovedModel
from ..requests import profile_request


class ReportErrorModel(ApprovedModel):
    """정상 모델 응답 일부를 바꾸어 보고서 오류를 재현한다.

    Args:
        error_kind: json, schema, missing, evidence 또는 semantic 오류 종류.
        bad_reports: 처음 몇 번의 검증 보고서를 잘못 반환할지 지정하는 수.

    Returns:
        ReportErrorModel: 검증 요청을 관찰하고 지정한 오류를 만드는 모의 모델.
    """

    def __init__(self, error_kind, bad_reports=1):
        """오류 주입 조건과 검증 호출 기록을 준비한다.

        Args:
            error_kind: 검증 응답에 주입할 오류 종류.
            bad_reports: 잘못된 검증 응답을 반환할 횟수.

        Returns:
            None: 내부 호출 기록과 오류 조건을 초기화한다.
        """
        super().__init__()
        self.error_kind = error_kind
        self.bad_reports = bad_reports
        self.verification_calls = []
        self.verification_exchanges = []
        self.dialogue_calls = 0

    async def generate(self, messages, *, purpose="dialogue"):
        """생성은 승인 원문을 사용하고 검증 응답에만 지정한 오류를 주입한다.

        Args:
            messages: 생성 또는 검증용 프롬프트.
            purpose: dialogue 또는 verification 호출 목적.

        Returns:
            str: 정상 생성 원문 또는 오류가 주입된 검증 보고서 문자열.
        """
        raw = await super().generate(messages, purpose=purpose)
        if purpose == "dialogue":
            self.dialogue_calls += 1
            return raw
        self.verification_calls.append(messages)
        output = self.verification_output(raw)
        self.verification_exchanges.append(
            {"input": redact(messages), "output": output}
        )
        return output

    def verification_output(self, raw):
        """오류 주입 조건에 맞춰 모의 검증 응답을 반환한다.

        Args:
            raw: 오류 주입 전 검증 응답 원문.

        Returns:
            str: 그래프에 반환할 검증 응답.
        """
        if len(self.verification_calls) > self.bad_reports:
            return raw
        if self.error_kind == "json":
            return "잘못된 JSON"
        data = json.loads(raw)
        if self.error_kind == "schema":
            del data["uncertain"]
        elif self.error_kind == "missing":
            data["checks"] = []
        elif self.error_kind == "evidence":
            data["checks"][0][2] = [999]
        elif self.error_kind == "semantic":
            data["has_unsupported_claims"] = True
        return json.dumps(data)


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def service(fixture_settings):
    """앱의 시작 절차를 실행해 그래프 테스트용 수사 서비스를 준비한다.

    Args:
        fixture_settings: 모의 모델 테스트 환경 설정.

    Returns:
        AsyncIterator: 초기화한 수사 서비스.
    """
    app = create_app(fixture_settings)
    async with app.router.lifespan_context(app):
        yield app.state.service


async def run_graph(settings, model, dialogue_request, request):
    """그래프 입출력과 검증 시도별 입출력을 pytest 보고서에 남긴다.

    Args:
        settings: 그래프 설정.
        model: 검증 시도를 기록하는 모의 모델.
        dialogue_request: 그래프에 전달할 대화 요청.
        request: 현재 테스트의 기록에 접근하는 pytest 객체.

    Returns:
        CharacterReplyResponse: 그래프가 반환한 최종 대화 응답.
    """
    exchange = {
        "stage": "validation_graph",
        "input": redact(dialogue_request.model_dump(mode="json")),
        "output": None,
        "verification_exchanges": model.verification_exchanges,
    }
    request.node.exchanges.append(exchange)
    try:
        response = await InterrogationGraph(settings, model).generate(dialogue_request)
    except HTTPException as error:
        exchange["output"] = {
            "status": error.status_code,
            "detail": redact(error.detail),
            "headers": redact(error.headers),
        }
        raise
    except Exception as error:
        exchange["output"] = {"error_type": type(error).__name__, "detail": str(error)}
        raise
    exchange["output"] = redact(response.model_dump(mode="json"))
    return response


@pytest.mark.parametrize("error_kind", ["json", "schema", "missing", "evidence"])
async def test_report_format_retry_keeps_same_candidate(service, request, error_kind):
    """보고서 오류만 재요청하고 후보 대사를 새로 생성하지 않는지 확인한다.

    Args:
        service: 초기화한 테스트용 수사 서비스.
        request: 현재 테스트의 보고서 기록을 제공하는 pytest 객체.
        error_kind: 처음 보고서에 주입할 형식 또는 근거 오류 종류.

    Returns:
        None: 같은 후보로 검증 두 번, 대사 생성 한 번인지 검사한다.
    """
    dialogue_request = profile_request(service)
    model = ReportErrorModel(error_kind)
    response = await run_graph(service.settings, model, dialogue_request, request)
    assert response.finish_reason == "stop"
    assert model.dialogue_calls == 1
    assert len(model.verification_calls) == 2
    contexts = [
        json.loads(messages[1]["content"]) for messages in model.verification_calls
    ]
    assert contexts[0]["candidate_sentences"] == contexts[1]["candidate_sentences"]
    assert "검증 형식 오류" in model.verification_calls[1][-1]["content"]


async def test_report_format_exhaustion_does_not_regenerate(service, request):
    """보고서 형식 오류의 상한을 소진하면 대사 재생성 없이 오류로 끝낸다.

    Args:
        service: 초기화한 테스트용 수사 서비스.
        request: 현재 테스트의 보고서 기록을 제공하는 pytest 객체.

    Returns:
        None: HTTP 502와 검증 오류 코드, 생성 한 번을 확인한다.
    """
    model = ReportErrorModel("json", bad_reports=99)
    with pytest.raises(HTTPException) as caught:
        await run_graph(service.settings, model, profile_request(service), request)
    assert caught.value.status_code == 502
    assert caught.value.headers["X-Generation-Error"] == "invalid_verification_json"
    assert model.dialogue_calls == 1
    assert len(model.verification_calls) == 2


async def test_semantic_rejection_regenerates_instead_of_retrying_report(
    service, request
):
    """의미상 거절은 검사표 재요청이 아닌 대사 재생성으로 처리한다.

    Args:
        service: 초기화한 테스트용 수사 서비스.
        request: 현재 테스트의 보고서 기록을 제공하는 pytest 객체.

    Returns:
        None: 생성과 검증이 각각 두 번이며 같은 후보 재검사 지시가 없는지 확인한다.
    """
    model = ReportErrorModel("semantic")
    response = await run_graph(
        service.settings, model, profile_request(service), request
    )
    assert response.finish_reason == "stop"
    assert model.dialogue_calls == 2
    assert len(model.verification_calls) == 2
    assert all(
        "검증 형식 오류" not in messages[-1]["content"]
        for messages in model.verification_calls
    )


async def test_batches_keep_entire_approval_context(service, request):
    """검사 항목을 나누어도 모든 배치에 원래 승인 계획을 유지한다.

    Args:
        service: 초기화한 테스트용 수사 서비스.
        request: 현재 테스트의 보고서 기록을 제공하는 pytest 객체.

    Returns:
        None: 두 문장을 나누어 검증해도 원래 사실 ID 전체가 확인되는지 검사한다.
    """
    dialogue_request = profile_request(service)
    settings = service.settings.model_copy(update={"verification_batch_size": 1})
    model = ReportErrorModel("json", bad_reports=0)
    response = await run_graph(settings, model, dialogue_request, request)
    assert response.used_fact_ids == dialogue_request.required_fact_ids
    contexts = [
        json.loads(messages[1]["content"]) for messages in model.verification_calls
    ]
    assert len(contexts) == 2
    assert [context["verification_units"][0]["index"] for context in contexts] == [0, 1]
    assert contexts[0]["approved_facts"] == contexts[1]["approved_facts"]
    assert len(contexts[0]["approved_facts"][0]["units"]) == 2
