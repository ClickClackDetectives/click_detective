"""증거 없는 자유 질문과 생성 재시도 계약을 실제 사건 데이터·3노드 그래프로 회귀 검사한다."""

import json
from uuid import uuid4

import pytest

from app.dialogue.interrogation_graph import InterrogationGraph, OutputRejected
from app.dialogue.semantic_verification import SemanticReport
from app.dialogue.verification_units import build_verification_units
from app.schemas import Interrogate


class RetryingModel:
    """첫 생성은 필수 뒷문장을 누락하고 다음 생성은 모두 포함하는 모의 모델.

    Args:
        없음.

    Returns:
        RetryingModel: 위 역할을 수행하도록 생성된 객체.
    """

    model_version = "regression-model"

    def __init__(self):
        """사용할 의존성과 초기 상태를 준비한다.

        Args:
            없음.

        Returns:
            None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.
        """
        self.generation_calls = []

    async def generate(self, messages, *, purpose="dialogue"):
        """실제 GPU 없이 생성 누락→검증 거절→올바른 평문 재생성을 재현한다.

        Args:
            messages: 모델에 전달할 역할별 프롬프트 목록.
            purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

        Returns:
            str: 호출 목적에 맞게 생성한 모델 출력 원문.
        """
        context = json.loads(messages[1]["content"])
        if "candidate_sentences" not in context:
            self.generation_calls.append(messages)
            required = context["required_sentences"]
            return (
                required[0] if len(self.generation_calls) == 1 else " ".join(required)
            )
        source = {
            unit["index"]: unit["text"]
            for fact in context["approved_facts"]
            for unit in fact["units"]
        }
        checks = []
        for unit in context["verification_units"]:
            parts = [
                part["id"]
                for part in context["candidate_sentences"]
                if source[unit["index"]] in part["text"]
            ]
            checks.append([unit["index"], bool(parts), parts])
        return json.dumps(
            {
                "checks": checks,
                "has_contradiction": False,
                "has_unsupported_claims": False,
                "history_consistent": True,
                "persona_consistent": True,
                "uncertain": False,
            }
        )


async def test_no_evidence_question_can_retry_as_plain_text(client):
    """강민호 면담 질문의 첫 필수 문장 누락을 평문 형식을 유지하며 복구한다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    service = client.app.state.service
    state = service.engine.initial(str(uuid4()))
    command = Interrogate(
        request_id=uuid4(),
        expected_revision=0,
        suspect_id="kang",
        question="와인잔에 무엇을 했는지 말해주세요",
    )
    plan = service.planner.prepare(state, command)
    request = service.dialogue_request(state, command, plan)
    model = RetryingModel()
    response = await InterrogationGraph(service.settings, model).generate(request)
    assert response.finish_reason == "stop"
    assert response.used_fact_ids == ["kang-meeting"]
    assert all(fact.text in response.reply for fact in request.allowed_facts)
    assert len(model.generation_calls) == 2
    retry_instruction = model.generation_calls[1][-1]["content"]
    assert "대사 원문만" in retry_instruction
    assert "JSON 형식도 지키세요" not in retry_instruction


def test_unknown_free_question_returns_neutral_without_model(
    api, client, game, monkeypatch
):
    """승인 정보가 없는 질문은 502·허구 생성 대신 기존 중립 정책으로 응답한다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        client: HTTP 요청을 실행하는 클라이언트.
        game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
        monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """

    class NeverModel:
        """호출되면 실패하는 모델로 빈 승인 경로의 GPU 미호출을 확인한다.

        Args:
            없음.

        Returns:
            NeverModel: 위 역할을 수행하도록 생성된 객체.
        """

        model_version = "never-called"

        async def generate(self, messages, *, purpose="dialogue"):
            """호출 목적에 맞는 모델 출력을 만들거나 검사용 실패를 발생시킨다.

            Args:
                messages: 모델에 전달할 역할별 프롬프트 목록.
                purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

            Returns:
                str: 호출 목적에 맞게 생성한 모델 출력 원문.
            """
            raise AssertionError("승인 사실이 없는 질문에 모델을 호출했습니다.")

    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(
        service, "graph", InterrogationGraph(service.settings, NeverModel())
    )
    response = api(
        "POST",
        "/v1/games/" + game["game_id"] + "/interrogations",
        {
            "request_id": str(uuid4()),
            "expected_revision": 0,
            "suspect_id": "kang",
            "question": "수학 문제를 풀어주세요",
        },
        game["game_token"],
    )
    assert response.status_code == 200
    assert response.json()["result"]["finish_reason"] == "fixed"
    assert response.json()["result"]["used_fact_ids"] == []
    assert response.json()["state"]["findingDetails"] == []


def test_false_verification_with_evidence_still_rejected(client):
    """검증 형식 안정화 과정에서도 false+근거 번호를 성공으로 수선하지 않는다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    service = client.app.state.service
    state = service.engine.initial(str(uuid4()))
    command = Interrogate(
        request_id=uuid4(),
        expected_revision=0,
        suspect_id="kang",
        question="자기소개를 해주세요",
    )
    request = service.dialogue_request(
        state, command, service.planner.prepare(state, command)
    )
    report = SemanticReport(
        checks=[
            (index, False, [0])
            for index, _ in enumerate(build_verification_units(request))
        ],
        has_contradiction=False,
        has_unsupported_claims=False,
        history_consistent=True,
        persona_consistent=True,
        uncertain=False,
    )
    with pytest.raises(OutputRejected, match="verification_evidence_mismatch"):
        InterrogationGraph._check_report_evidence(
            report, request, request.allowed_facts[0].text
        )
