"""계정용 경로가 서비스 키와 사용자 인증을 요구하는지 검사한다."""


def test_investigations_require_service_key(client):
    """수사 목록 요청에 서버 인증이 없으면 거부한다.

    Args:
        client: fixture FastAPI 클라이언트.

    Returns:
        None: 반환값 없음.
    """
    response = client.get("/v1/investigations")
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "SERVICE_AUTH_REQUIRED"


def test_unconfigured_account_mode_does_not_resume_anonymous_game(api, game):
    """계정 접근 요청은 같은 수사의 익명 토큰으로 대체되지 않는다.

    Args:
        api: 서비스 인증을 붙이는 요청 도우미.
        game: 토큰이 발급된 기존 익명 수사.

    Returns:
        None: 반환값 없음.
    """
    response = api(
        "GET",
        f"/v1/games/{game['game_id']}",
        game_token=game["game_token"],
        headers={"X-Access-Token": "unverified"},
    )
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "AUTH_DISABLED"


def test_claim_route_requires_service_key(client):
    """익명 수사 연결을 외부 서비스 요청으로 직접 호출하면 거부한다.

    Args:
        client: fixture FastAPI 클라이언트.

    Returns:
        None: 반환값 없음.
    """
    response = client.post(
        "/v1/investigations/claim",
        json={"game_id": "0993248c-0a31-46b5-8c83-b9a3b500401e"},
        headers={"X-Game-Token": "unverified"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "SERVICE_AUTH_REQUIRED"


def test_confirmed_change_does_not_call_abort(api, client, game, monkeypatch):
    """성공 응답을 확정한 뒤 실패 전용 예약 정리를 호출하지 않는다.

    Args:
        api: 서비스 인증을 붙이는 요청 도우미.
        client: 수사 서비스를 사용하는 fixture 클라이언트.
        game: 변경할 익명 수사.
        monkeypatch: 실패가 발생하는 예약 정리를 설치하는 테스트 도구.

    Returns:
        None: 확정된 변경의 응답을 검사한다.
    """
    from uuid import uuid4

    def unavailable_abort(command, reservation):
        """예약 정리 중 접속 오류를 재현한다.

        Args:
            command: 앞서 실행한 수사 변경 입력.
            reservation: 앞서 얻은 실행권.

        Returns:
            None: 호출 시 오류가 발생한다.
        """
        raise RuntimeError("abort storage is unavailable")

    monkeypatch.setattr(client.app.state.service.repository, "abort", unavailable_abort)
    response = api(
        "PUT",
        f"/v1/games/{game['game_id']}/notes",
        {"request_id": str(uuid4()), "expected_revision": 0, "text": "새 메모"},
        game_token=game["game_token"],
    )
    assert response.status_code == 200
    assert response.json()["state"]["revision"] == 1
