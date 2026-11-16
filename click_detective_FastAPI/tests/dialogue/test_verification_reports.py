"""검증 책임 분리 후에도 배치·보고서 재요청·의미상 거절 정책을 유지한다."""

import json
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.dialogue.interrogation_graph import InterrogationGraph
from app.investigation.schemas import Interrogate

from .models import ApprovedModel


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


def profile_request(client):
    """두 문장으로 구성된 실제 인물 소개를 승인 요청으로 만든다.

    Args:
        client: fixture 모드로 실행한 FastAPI 테스트 클라이언트.

    Returns:
        CharacterReplyRequest: 윤재혁 소개의 두 문장을 필수로 포함하는 요청.
    """
    service = client.app.state.service
    state = service.engine.initial(str(uuid4()))
    command = Interrogate(
        request_id=uuid4(),
        expected_revision=0,
        suspect_id="yoon",
        question="자기소개를 해주세요.",
    )
    return service.dialogue_request(
        state, command, service.planner.prepare(state, command)
    )


@pytest.mark.parametrize("error_kind", ["json", "schema", "missing", "evidence"])
async def test_report_format_retry_keeps_same_candidate(client, error_kind):
    """보고서 오류만 재요청하고 후보 대사를 새로 생성하지 않는지 확인한다.

    Args:
        client: 테스트 앱과 실행 설정을 제공하는 클라이언트.
        error_kind: 처음 보고서에 주입할 형식 또는 근거 오류 종류.

    Returns:
        None: 같은 후보로 검증 두 번, 대사 생성 한 번인지 검사한다.
    """
    request = profile_request(client)
    model = ReportErrorModel(error_kind)
    response = await InterrogationGraph(
        client.app.state.service.settings, model
    ).generate(request)
    assert response.finish_reason == "stop"
    assert model.dialogue_calls == 1
    assert len(model.verification_calls) == 2
    contexts = [
        json.loads(messages[1]["content"]) for messages in model.verification_calls
    ]
    assert contexts[0]["candidate_sentences"] == contexts[1]["candidate_sentences"]
    assert "검증 형식 오류" in model.verification_calls[1][-1]["content"]


async def test_report_format_exhaustion_does_not_regenerate(client):
    """보고서 형식 오류의 상한을 소진하면 대사 재생성 없이 오류로 끝낸다.

    Args:
        client: 복구가 비활성화된 fixture 앱 클라이언트.

    Returns:
        None: HTTP 502와 검증 오류 코드, 생성 한 번을 확인한다.
    """
    model = ReportErrorModel("json", bad_reports=99)
    graph = InterrogationGraph(client.app.state.service.settings, model)
    with pytest.raises(HTTPException) as caught:
        await graph.generate(profile_request(client))
    assert caught.value.status_code == 502
    assert caught.value.headers["X-Generation-Error"] == "invalid_verification_json"
    assert model.dialogue_calls == 1
    assert len(model.verification_calls) == 2


async def test_semantic_rejection_regenerates_instead_of_retrying_report(client):
    """의미상 거절은 검사표 재요청이 아닌 대사 재생성으로 처리한다.

    Args:
        client: 두 번의 대사 생성을 허용하는 테스트 앱 클라이언트.

    Returns:
        None: 생성과 검증이 각각 두 번이며 같은 후보 재검사 지시가 없는지 확인한다.
    """
    model = ReportErrorModel("semantic")
    response = await InterrogationGraph(
        client.app.state.service.settings, model
    ).generate(profile_request(client))
    assert response.finish_reason == "stop"
    assert model.dialogue_calls == 2
    assert len(model.verification_calls) == 2
    assert all(
        "검증 형식 오류" not in messages[-1]["content"]
        for messages in model.verification_calls
    )


async def test_batches_keep_entire_approval_context(client):
    """검사 항목을 나누어도 모든 배치에 원래 승인 계획을 유지한다.

    Args:
        client: 기본 설정을 제공하는 테스트 앱 클라이언트.

    Returns:
        None: 두 문장을 나누어 검증해도 원래 사실 ID 전체가 확인되는지 검사한다.
    """
    request = profile_request(client)
    settings = client.app.state.service.settings.model_copy(
        update={"verification_batch_size": 1}
    )
    model = ReportErrorModel("json", bad_reports=0)
    response = await InterrogationGraph(settings, model).generate(request)
    assert response.used_fact_ids == request.required_fact_ids
    contexts = [
        json.loads(messages[1]["content"]) for messages in model.verification_calls
    ]
    assert len(contexts) == 2
    assert [context["verification_units"][0]["index"] for context in contexts] == [0, 1]
    assert contexts[0]["approved_facts"] == contexts[1]["approved_facts"]
    assert len(contexts[0]["approved_facts"][0]["units"]) == 2
