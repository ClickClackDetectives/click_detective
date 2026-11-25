"""dialogue/test_runtime.py의 회귀 동작을 확인한다."""

import asyncio
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.dialogue.interrogation_graph import InterrogationGraph
from app.dialogue.schemas import CharacterReplyResponse
from app.investigation.api.schemas import Interrogate, Notes

from .models import ApprovedModel


async def test_three_agents_execute_with_backend_approval(client, game, tmp_path):
    """전처리·생성·검증 노드와 내부 승인 DTO가 실제로 연결되는지 검사한다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.
        game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
        tmp_path: 이 요청의 실행 진단을 저장할 임시 경로.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    service = client.app.state.service
    state = service.read(game["game_id"], game["game_token"])
    command = Interrogate(
        request_id=uuid4(),
        expected_revision=0,
        suspect_id="yoon",
        question="그날 밤의 동선을 알려주세요.",
        topic_id="movement",
    )
    plan = service.planner.prepare(state, command)
    request = service.dialogue_request(state, command, plan)
    approved_ids = [fact.id for fact in request.allowed_facts]
    assert len(approved_ids) > service.settings.rag_top_k
    model = ApprovedModel()
    trace_path = tmp_path / "trace.jsonl"
    settings = service.settings.model_copy(
        update={"diagnostics_enabled": True, "diagnostics_path": trace_path}
    )
    graph = InterrogationGraph(settings, model)
    assert {"preprocess_agent", "inference_agent", "validation_agent"} <= set(
        graph.graph.get_graph().nodes
    )
    response = await graph.generate(request)
    assert response.finish_reason == "stop"
    assert response.used_fact_ids == approved_ids
    assert len(model.calls) == 2
    assert [fact["id"] for fact in model.calls[0]["approved_facts"]] == approved_ids
    assert service.read(game["game_id"], game["game_token"])["questions"] == 0


def test_generation_failure_charges_the_question_once(api, client, game, monkeypatch):
    """받아들인 질문은 모델 실패 및 동일 요청 재전송에도 한 번만 차감한다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        client: HTTP 요청을 실행하는 클라이언트.
        game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
        monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """

    class FailingGraph:
        """검증 또는 추론 실패를 HTTP 오류로 재현한다.

        Args:
            없음.

        Returns:
            FailingGraph: 위 역할을 수행하도록 생성된 객체.
        """

        async def generate(self, request):
            """실제 GPU를 사용하지 않는다.

            Args:
                request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

            Returns:
                str: 호출 목적에 맞게 생성한 모델 출력 원문.
            """
            raise HTTPException(502, "Generation service failed")

    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service, "graph", FailingGraph())
    path = f"/v1/games/{game['game_id']}"
    body = {
        "request_id": str(uuid4()),
        "expected_revision": 0,
        "suspect_id": "kang",
        "question": "자기소개를 해주세요.",
    }
    for _ in range(2):
        assert (
            api("POST", path + "/interrogations", body, game["game_token"]).status_code
            == 502
        )
    restored = api("GET", path, game_token=game["game_token"]).json()["state"]
    assert restored["questions"] == 1
    assert restored["revision"] == 1
    assert restored["messages"] == []


async def test_state_change_during_generation_rejects_stale_reply(
    client, game, monkeypatch
):
    """생성 중 다른 행동이 확정되면 오래된 대사를 저장하지 않는다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.
        game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
        monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    started, release = asyncio.Event(), asyncio.Event()

    class WaitingGraph:
        """모델 대기 동안 다른 API의 상태 변경이 가능한 상황을 재현한다.

        Args:
            없음.

        Returns:
            WaitingGraph: 위 역할을 수행하도록 생성된 객체.
        """

        async def generate(self, request):
            """승인 원문을 응답하더라도 revision이 달라지면 저장 단계에서 거절돼야 한다.

            Args:
                request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

            Returns:
                str: 호출 목적에 맞게 생성한 모델 출력 원문.
            """
            started.set()
            await release.wait()
            return CharacterReplyResponse(
                request_id=request.request_id,
                suspect_id=request.suspect_id,
                state_revision=request.state_revision,
                reply=" ".join(fact.text for fact in request.allowed_facts),
                used_fact_ids=request.required_fact_ids,
                model_version="waiting-contract",
                finish_reason="stop",
            )

    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service, "graph", WaitingGraph())
    command = Interrogate(
        request_id=uuid4(),
        expected_revision=0,
        suspect_id="kang",
        question="자기소개를 해주세요.",
    )
    task = asyncio.create_task(
        service.change(game["game_id"], game["game_token"], command, "interrogate")
    )
    try:
        await asyncio.wait_for(started.wait(), timeout=2)
        assert service.read(game["game_id"], game["game_token"])["questions"] == 1
        with pytest.raises(HTTPException) as duplicate:
            await service.change(
                game["game_id"], game["game_token"], command, "interrogate"
            )
        assert duplicate.value.status_code == 409
        await service.change(
            game["game_id"],
            game["game_token"],
            Notes(request_id=uuid4(), expected_revision=1, text="생성 중 저장"),
            "notes",
        )
    finally:
        release.set()
    with pytest.raises(HTTPException) as stale:
        await task
    assert stale.value.status_code == 409
    state = service.read(game["game_id"], game["game_token"])
    assert state["notes"] == "생성 중 저장"
    assert state["revision"] == 2 and state["questions"] == 1


def test_resubmitting_identical_question_as_new_action_charges_again(api, game):
    """같은 질문을 새로 제출하면 새 심문으로 차감하고 통신 재시도는 중복 차감하지 않는다.

    Args:
        api: 수사 API를 호출하는 테스트 도우미.
        game: 새 수사의 ID, 접근 토큰과 상태.

    Returns:
        None: 동일 질문을 두 번 제출한 뒤 저장된 심문 횟수를 검사한다.
    """
    path = f"/v1/games/{game['game_id']}/interrogations"
    body = {
        "request_id": str(uuid4()),
        "expected_revision": 0,
        "suspect_id": "kang",
        "question": "자기소개를 해주세요.",
    }
    first = api("POST", path, body, game["game_token"]).json()
    assert first["state"]["questions"] == 1
    replay = api("POST", path, body, game["game_token"]).json()
    assert replay == first

    second_body = {
        **body,
        "request_id": str(uuid4()),
        "expected_revision": first["state"]["revision"],
    }
    second = api("POST", path, second_body, game["game_token"]).json()
    assert second["state"]["questions"] == 2
    assert [m["text"] for m in second["state"]["messages"] if m["role"] == "user"] == [
        body["question"],
        body["question"],
    ]
