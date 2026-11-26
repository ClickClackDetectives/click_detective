"""서버 간 API 인증을 공통으로 제공한다."""

import hmac

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)


async def authenticate(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)
):
    """Next.js 서버 전용 API 키를 검사한다. 브라우저에 이 키를 전달하지 않는다.

    Args:
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
        credentials (HTTPAuthorizationCredentials | None): Authorization 헤더에서 읽은 Bearer 인증 정보.

    Returns:
        None: 반환값 없음.
    """
    if credentials is None or not hmac.compare_digest(
        credentials.credentials, request.app.state.settings.api_key
    ):
        raise HTTPException(
            401,
            {"code": "SERVICE_AUTH_REQUIRED", "message": "서비스 인증이 필요합니다."},
            headers={"WWW-Authenticate": "Bearer"},
        )
