"""게임에서 전송한 유효 질문은 모델 실패·쟁점 여부와 무관하게 답변을 확정한다."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.dialogue.services.preprocess_agent.rag.dialogue_fact_retriever import OVERVIEW
from app.dialogue.services.reply.dialogue_interrogation_graph import InterrogationGraph
from app.runtime.runtime_settings import Settings

from .test_question_search import ask
from .test_question_search import vector_route as vector_route


def test_generation_failure_preserves_graph_retrieval(
    api, game, monkeypatch, vector_route
):
    """검색을 완료했어도 생성 실패가 승인 사실의 전달로 기록되지 않는지 확인한다.

    Args:
        api: 심문 API 호출 함수.
        game: 새 수사 상태.
        monkeypatch: 생성 모델의 장애를 주입하는 도구.
        vector_route: 검색기와 생성 모델을 사용하도록 설정한 서비스.

    Returns:
        None: 검색을 실행한 뒤 중립 응답만 확정하는지 확인한다.
    """
    service, index, model = vector_route
    index.scores[OVERVIEW] = 0.93
    monkeypatch.setattr(service.settings, "fallback_on_error", True)
    monkeypatch.setattr(model, "generate", AsyncMock(side_effect=RuntimeError))
    question = "그날 밤 어떤 순서로 움직였나요?"
    result = ask(api, game, question)
    recorded = service.read(game["game_id"], game["game_token"])["statements"]
    assert result["finish_reason"] == "neutral"
    assert result["used_fact_ids"] == []
    assert not recorded
    assert index.questions == [question]


@pytest.mark.parametrize(
    "failure",
    [
        HTTPException(502, "Generation service failed"),
        HTTPException(504, "Generation timed out"),
        HTTPException(422, "Approved context exceeds local token budget"),
        RuntimeError("model runtime failed"),
        ValueError("invalid generated output"),
    ],
)
def test_generation_failure_commits_neutral_reply_once(
    api, client, game, monkeypatch, failure
):
    """모델 실패는 중립 응답으로 복구하며 같은 UUID를 중복 소비하지 않는다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        client: HTTP 요청을 실행하는 클라이언트.
        game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
        monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.
        failure: 테스트에서 재현할 실패 종류.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """

    class FailingGraph:
        """모델 경로의 실패만 주입하고 승인·저장 로직은 실제 코드를 사용한다.

        Args:
            없음.

        Returns:
            FailingGraph: 위 역할을 수행하도록 생성된 객체.
        """

        calls = 0

        async def generate(self, request):
            """호출 목적에 맞는 모델 출력을 만들거나 검사용 실패를 발생시킨다.

            Args:
                request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

            Returns:
                str: 호출 목적에 맞게 생성한 모델 출력 원문.
            """
            self.calls += 1
            raise failure

    graph = FailingGraph()
    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service.settings, "fallback_on_error", True)
    monkeypatch.setattr(service.reply_service, "graph", graph)
    path = "/v1/games/" + game["game_id"] + "/interrogations"
    body = {
        "request_id": str(uuid4()),
        "expected_revision": 0,
        "suspect_id": "kang",
        "question": "자기소개를 해주세요.",
    }
    response = api("POST", path, body, game["game_token"])
    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["finish_reason"] == "neutral"
    assert payload["result"]["used_fact_ids"] == []
    assert payload["state"]["questions"] == 1
    assert payload["state"]["revision"] == 2
    assert len(payload["state"]["messages"]) == 2
    assert payload["state"]["findingDetails"] == []
    assert api("POST", path, body, game["game_token"]).json() == payload
    assert graph.calls == 1


def test_failed_generated_admission_does_not_unlock_finding(
    api, client, play, monkeypatch
):
    """중립 응답은 제시 조건을 통과한 쟁점도 공개하지 않는다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        client: HTTP 요청을 실행하는 클라이언트.
        play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.
        monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """

    class FailingGraph:
        """모델 실패를 재현하여 복구와 상태 보존을 검사하는 모의 그래프다.

        Args:
            없음.

        Returns:
            FailingGraph: 위 역할을 수행하도록 생성된 객체.
        """

        async def generate(self, request):
            """호출 목적에 맞는 모델 출력을 만들거나 검사용 실패를 발생시킨다.

            Args:
                request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

            Returns:
                str: 호출 목적에 맞게 생성한 모델 출력 원문.
            """
            raise RuntimeError("inference unavailable")

    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service.settings, "fallback_on_error", True)
    monkeypatch.setattr(service.reply_service, "graph", FailingGraph())
    play.act("examinations", evidence_id="S-Y")
    response = play.act(
        "interrogations",
        suspect_id="yoon",
        question="장부의 경위를 설명하세요.",
        material_id="S-Y",
    )
    assert response["result"]["finish_reason"] == "neutral"
    assert response["state"]["revealed"] == []
    assert response["result"]["used_fact_ids"] == []
    assert response["state"]["questions"] == 1
    assert response["state"]["findingDetails"] == []


async def test_real_graph_rejection_returns_neutral(client, monkeypatch):
    """출력 형식을 거절한 그래프는 중립 응답을 반환한다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.
        monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """

    class InvalidModel:
        """출력 오류를 재현하는 모의 모델이다.

        Args:
            없음.

        Returns:
            InvalidModel: 위 역할을 수행하도록 생성된 객체.
        """

        model_version = "invalid-output-test"

        async def generate(self, messages, *, purpose="dialogue"):
            """호출 목적에 맞는 모델 출력을 만들거나 검사용 실패를 발생시킨다.

            Args:
                messages: 모델에 전달할 역할별 프롬프트 목록.
                purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

            Returns:
                str: 호출 목적에 맞게 생성한 모델 출력 원문.
            """
            return "{invalid output"

    from app.investigation.dto.investigation_command_dto import Interrogate

    service = client.app.state.service
    monkeypatch.setattr(service.settings, "fallback_on_error", True)
    state = service.engine.initial(str(uuid4()))
    command = Interrogate(
        request_id=uuid4(),
        expected_revision=0,
        suspect_id="kang",
        question="자기소개를 해주세요.",
    )
    request = service.dialogue_request(
        state, command, service.planner.prepare(state, command)
    )
    response = await InterrogationGraph(service.settings, InvalidModel()).generate(
        request
    )
    assert response.finish_reason == "neutral"
    assert response.used_fact_ids == []


def test_default_player_policy_enables_reply_recovery():
    """신규 실행도 기본적으로 생성 오류를 플레이어에게 502로 내보내지 않는다.

    Args:
        없음.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    config = Settings(api_key="test-api-secret-long-enough", _env_file=None)
    assert config.fallback_on_error is True
