"""실제 사건 데이터로 초기·소수 근거 고발과 부족한 입증의 채점을 검사한다."""

import json
from uuid import uuid4

import pytest

from app.runtime.runtime_settings import PROJECT_ROOT


def selections():
    """테스트만 서버 비공개 정답을 읽어 선택 채점과 근거 채점을 분리한다.

    Args:
        없음.

    Returns:
        테스트만 서버 비공개 정답을 읽어 선택 채점과 근거 채점을 분리한다.
    """
    solution = json.loads(
        (PROJECT_ROOT / "data/case/solution.private.json").read_text()
    )["solution"]
    return {
        "suspect_id": solution["suspectId"],
        "motive": solution["motive"],
        "method": solution["method"],
    }


@pytest.mark.parametrize("include_empty_evidence", [False, True])
def test_initial_game_can_accuse_without_evidence(api, game, include_empty_evidence):
    """1차 조사·쟁점 0·추론 0이어도 제출하고, 입증 부족은 채점으로 처리한다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
        include_empty_evidence: 모의 보고서에 잘못된 빈 근거를 포함할지 여부.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    state = game["state"]
    assert state["phase"] == 1
    assert state["availableActions"]["accuse"] is True
    assert state["accusationReadiness"]["eligible"] is True
    body = {"request_id": str(uuid4()), "expected_revision": 0, **selections()}
    if include_empty_evidence:
        body["evidence_ids"] = []
    path = "/v1/games/" + game["game_id"]
    response = api("POST", path + "/accusations", body, game["game_token"])
    assert response.status_code == 200
    verdict = response.json()["result"]
    assert verdict["score"] == 75
    assert verdict["correct"] is False
    assert verdict["submittedEvidenceIds"] == []
    assert verdict["checks"][-1]["correct"] is False
    assert verdict["evidenceAssessment"]["missing"]
    assert response.json()["state"]["availableActions"]["accuse"] is False
    assert (
        api("POST", path + "/accusations", body, game["game_token"]).json()
        == response.json()
    )
    repeated = api(
        "POST",
        path + "/accusations",
        body | {"request_id": str(uuid4()), "expected_revision": 1},
        game["game_token"],
    )
    assert repeated.status_code == 409
    restored = api("GET", path, game_token=game["game_token"]).json()["state"]
    assert restored["verdict"] == response.json()["state"]["verdict"]


def test_single_earned_inference_can_be_submitted(play):
    """실제 1차 추론 하나만 확보해 제출해도 최소 5개 제한에 막히지 않는다.

    Args:
        play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    rules = json.loads(
        (PROJECT_ROOT / "data/case/inferences.private.json").read_text()
    )["rules"]
    rule = next(
        r
        for r in rules
        if r["phase"] == 1 and all(s["kind"] == "evidence" for s in r["sources"])
    )
    for source in rule["sources"]:
        play.act("examinations", evidence_id=source["id"])
    play.act("inferences", sources=rule["sources"])
    ids = list(play.state["derivedEvidence"])
    assert len(ids) == 1
    verdict = play.act("accusations", **selections(), evidence_ids=ids)["result"]
    assert verdict["submittedEvidenceIds"] == ids
    assert verdict["checks"][-1]["correct"] is False


def test_unearned_inference_still_rejected_without_consuming_state(api, game):
    """제출 자유가 존재하지 않는 추론을 근거로 제출할 권한까지 주지는 않는다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    response = api(
        "POST",
        "/v1/games/" + game["game_id"] + "/accusations",
        {
            "request_id": str(uuid4()),
            "expected_revision": 0,
            **selections(),
            "evidence_ids": ["derived-reset-impact-fit"],
        },
        game["game_token"],
    )
    assert response.status_code == 422
    state = api(
        "GET", "/v1/games/" + game["game_id"], game_token=game["game_token"]
    ).json()["state"]
    assert state["verdict"] is None
    assert state["revision"] == 0
