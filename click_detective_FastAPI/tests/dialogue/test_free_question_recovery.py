"""증거 없는 자유 질문과 생성 재시도 계약을 실제 사건 데이터·3노드 그래프로 회귀 검사한다."""

import json
from uuid import uuid4

from app.dialogue.services.reply.dialogue_interrogation_graph import InterrogationGraph


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


def test_unknown_free_question_returns_neutral(api, client, game, monkeypatch):
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
        """근거 없는 후보 대사와 거절 판정을 제공한다.

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
            if purpose == "dialogue":
                return "비밀 문서를 발견했습니다."
            return '{"allowed": false}'

    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(
        service.reply_service,
        "graph",
        InterrogationGraph(service.settings, NeverModel()),
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
    assert response.json()["result"]["finish_reason"] == "neutral"
    assert response.json()["result"]["used_fact_ids"] == []
    assert response.json()["state"]["findingDetails"] == []
