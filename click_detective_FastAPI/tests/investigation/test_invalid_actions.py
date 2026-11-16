"""investigation/test_invalid_actions.py의 회귀 동작을 확인한다."""

from uuid import uuid4


def test_unearned_sources_and_invalid_actions(api, play):
    """수집하지 않은 출처·미래 단계·승인 사실 주입을 거절한다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    base = "/v1/games/" + play.game_id
    common = {"expected_revision": 0}
    assert (
        api(
            "POST",
            base + "/examinations",
            common | {"request_id": str(uuid4()), "evidence_id": "2-03"},
            play.token,
        ).status_code
        == 404
    )
    assert (
        api(
            "POST",
            base + "/inferences",
            common
            | {
                "request_id": str(uuid4()),
                "sources": [
                    {"kind": "evidence", "id": "1-02"},
                    {"kind": "testimony", "id": "kang-admit-gang_drug"},
                ],
            },
            play.token,
        ).status_code
        == 422
    )
    assert (
        api(
            "POST",
            base + "/phase-transitions",
            common | {"request_id": str(uuid4())},
            play.token,
        ).status_code
        == 422
    )
    assert (
        api(
            "POST",
            base + "/interrogations",
            common
            | {
                "request_id": str(uuid4()),
                "suspect_id": "kang",
                "question": "질문",
                "allowed_facts": [],
            },
            play.token,
        ).status_code
        == 422
    )
    assert play.state["questions"] == 0
