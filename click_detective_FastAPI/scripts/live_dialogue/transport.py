"""HTTP 왕복 기록과 비밀값 마스킹을 담당한다."""

from time import perf_counter

import httpx

from .errors import LiveTestFailure


class LiveTransport:
    """실서버 HTTP 요청과 응답을 기록하고 비밀값을 가린다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.
        api_key: 서버 인증에 사용할 비밀 API 키.

    Returns:
        LiveTransport: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, client, api_key):
        """사용할 의존성과 초기 상태를 준비한다.

        Args:
            client: HTTP 요청을 실행하는 클라이언트.
            api_key: 서버 인증에 사용할 비밀 API 키.

        Returns:
            None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.
        """
        self.client = client
        self.secrets = [api_key]
        self.headers = {"Authorization": "Bearer " + api_key}

    def redact(self, value):
        """헤더·토큰 필드와 문자열에 포함된 실제 비밀값까지 가린다.

        Args:
            value: 검사·변환하거나 비밀값을 가릴 입력 값.

        Returns:
            입력과 같은 구조의 값: 인증 정보와 알려진 비밀값을 가린 결과.
        """
        if isinstance(value, dict):
            return {
                key: "[REDACTED]"
                if key.lower()
                in {"authorization", "x-game-token", "game_token", "api_key"}
                else self.redact(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self.redact(item) for item in value]
        if isinstance(value, str):
            for secret in self.secrets:
                if secret:
                    value = value.replace(secret, "[REDACTED]")
        return value

    def exchange(
        self, rows, method, path, body=None, token=None, purpose="preparation"
    ):
        """assertion 전에 왕복을 기록한다. 타임아웃도 요청 UUID·본문을 남긴다.

        Args:
            rows: HTTP 왕복 기록을 추가할 목록.
            method: HTTP 요청 메서드. 예: GET, POST.
            path: 저장 파일 경로나 HTTP 요청 경로.
            body: 전송하거나 비교할 JSON 요청 본문.
            token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.
            purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

        Returns:
            dict: 성공한 HTTP 응답의 JSON 객체. 왕복 기록은 rows에도 추가한다.
        """
        headers = self.headers | ({"X-Game-Token": token} if token else {})
        row = {
            "purpose": purpose,
            "input": {"method": method, "path": path, "headers": headers, "body": body},
            "output": None,
        }
        rows.append(row)
        started = perf_counter()
        try:
            response = self.client.request(
                method,
                path,
                headers=headers,
                **({"json": body} if body is not None else {}),
            )
            try:
                output = response.json()
            except ValueError:
                output = {"text": response.text}
            # 새 수사 응답의 토큰을 report에 보관하기 전에 마스킹 목록에 추가한다.
            if isinstance(output, dict) and isinstance(output.get("game_token"), str):
                self.secrets.append(output["game_token"])
            row["output"] = {
                "status": response.status_code,
                "body": output,
                "generation_error": response.headers.get("X-Generation-Error"),
            }
            if response.status_code != 200:
                code = response.headers.get("X-Generation-Error") or (
                    output.get("detail") if isinstance(output, dict) else None
                )
                raise LiveTestFailure(
                    f"{method} {path}: HTTP {response.status_code}, 원인: {code}"
                )
            if not isinstance(output, dict):
                raise LiveTestFailure("JSON 객체 응답이 아닙니다.")
            return output
        except httpx.RequestError as error:
            row["transport_error"] = type(error).__name__
            raise LiveTestFailure(
                f"{type(error).__name__}: 응답을 확정할 수 없습니다. 기록된 UUID로 서버 상태·진단을 확인하세요."
            ) from error
        finally:
            row["elapsed_ms"] = round((perf_counter() - started) * 1000, 2)
