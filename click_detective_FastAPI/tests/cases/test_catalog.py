"""cases/test_catalog.py의 회귀 동작을 확인한다."""

import json
from uuid import uuid4

import pytest


def test_public_data_and_assets(api):
    """사건·프로필·소개 자산은 조회하고 비공개 정답·증거 이미지는 막는다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    assert api("GET", "/healthz", authenticated=False).json() == {"status": "ok"}
    catalog = api("GET", "/v1/catalog").json()
    assert len(catalog["characters"]) == 5
    assert "solution" not in catalog
    assert api("GET", "/v1/cases").json()["cases"][0]["case_id"] == catalog["caseId"]
    assert api("GET", "/v1/cases/" + catalog["caseId"]).status_code == 200
    assert api("GET", "/v1/cases/unknown").status_code == 404
    assert api("GET", catalog["characters"][0]["portrait"]).status_code == 200
    assert api("GET", "/v1/assets/assets/evidence/1-01.png").status_code == 404
    assert api("GET", "/v1/assets/../case/solution.private.json").status_code == 404
    assert (
        api(
            "GET",
            "/v1/assets/assets/intro/thirteenth-bell-opening-v3-quiet.mp4",
            headers={"Range": "bytes=0-99"},
        ).status_code
        == 206
    )


def test_game_ownership_and_hidden_content(api, game):
    """게임 ID를 알아도 토큰 없이 읽지 못하고 미열람 본문도 제공하지 않는다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    base = "/v1/games/" + game["game_id"]
    assert api("GET", base).status_code == 404
    assert api("GET", base, game_token="wrong").status_code == 404
    state = api("GET", base, game_token=game["game_token"]).json()["state"]
    assert state["revision"] == 0 and state["progress"]["percent"] == 0
    assert state["findingDetails"] == []
    assert "explanation" not in json.dumps(state)
    assert (
        api(
            "GET", base + "/materials/evidence:1-01", game_token=game["game_token"]
        ).status_code
        == 422
    )
    assert api("GET", base + "/findings", game_token=game["game_token"]).json() == {
        "findings": []
    }


def test_create_idempotency_and_conflict(api):
    """생성 요청을 재전송해도 같은 수사·토큰을 반환하고 다른 내용은 충돌한다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    catalog = api("GET", "/v1/catalog").json()
    body = {"request_id": str(uuid4()), "scenario_version": catalog["scenarioVersion"]}
    first = api("POST", "/v1/games", body)
    assert api("POST", "/v1/games", body).json() == first.json()
    assert api("POST", "/v1/games", body | {"case_id": "unknown"}).status_code in {
        404,
        409,
    }
    assert (
        api("POST", "/v1/games", body | {"scenario_version": "old"}).status_code == 409
    )


@pytest.mark.parametrize(
    "path",
    [
        "/v1/catalog",
        "/v1/cases",
        "/v1/cases/thirteenth-bell-v1",
        "/v1/assets/hotel.jpg",
    ],
)
def test_authentication(api, path):
    """데이터·자산도 서버 전용 서비스 인증을 요구한다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        path: 저장 파일 경로나 HTTP 요청 경로.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    assert api("GET", path, authenticated=False).status_code == 401
    assert (
        api("GET", path, headers={"Authorization": "Bearer wrong"}).status_code == 401
    )
