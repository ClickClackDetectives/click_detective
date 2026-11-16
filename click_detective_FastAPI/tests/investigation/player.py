"""사용자 행동 API로만 수사를 진행하는 테스트 도우미다."""

from uuid import uuid4


class Player:
    """게임 상태를 조작하지 않고 사용자 행동 API로만 진행한다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

    Returns:
        Player: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, api, game):
        """API와 초기 수사 상태를 보관한다.

        Args:
            api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
            game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

        Returns:
            None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.
        """
        self.api = api
        self.state = game["state"]
        self.game_id = game["game_id"]
        self.token = game["game_token"]

    def act(self, endpoint, **fields):
        """새 요청 UUID·서버 revision을 넣고 갱신 상태를 적용한다.

        Args:
            endpoint: 요청할 수사 행동 API의 마지막 경로.
            fields: 행동 요청에 추가할 입력 필드.

        Returns:
            dict: 행동의 결과와 최신 공개 상태. 도우미가 보관한 상태도 갱신한다.
        """
        body = {
            "request_id": str(uuid4()),
            "expected_revision": self.state["revision"],
            **fields,
        }
        response = self.api(
            "PUT" if endpoint == "notes" else "POST",
            f"/v1/games/{self.game_id}/{endpoint}",
            body,
            self.token,
        )
        assert response.status_code == 200, (endpoint, response.text)
        self.state = response.json()["state"]
        return response.json()
