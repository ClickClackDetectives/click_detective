"""앱 수명 동안 PostgreSQL 인증 서비스를 구성하고 제공한다."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Request

from app.auth.services.auth_errors import auth_error
from app.auth.services.auth_service import AuthService
from app.runtime.runtime_settings import Settings


@asynccontextmanager
async def open_auth_service(config: Settings) -> AsyncIterator[AuthService | None]:
    """계정 인증 설정이 있으면 서비스를 열고 앱 종료 시 연결을 해제한다.

    Args:
        config: PostgreSQL 연결 문자열과 JWT 키를 제공하는 앱 설정.

    Returns:
        AsyncIterator[AuthService | None]: 앱 수명의 인증 서비스 또는 인증 미설정 시 None.
    """
    if config.postgres_dsn is None:
        yield None
        return
    service = await asyncio.to_thread(
        AuthService,
        config.postgres_dsn.get_secret_value(),
        config.auth_jwt_secret.get_secret_value(),
    )
    try:
        yield service
    finally:
        await asyncio.to_thread(service.close)


def get_auth_service(request: Request) -> AuthService:
    """FastAPI 앱의 인증 서비스가 준비됐는지 확인한다.

    Args:
        request: 인증 서비스를 보관하는 FastAPI 앱의 요청.

    Returns:
        AuthService: 앱 기동 시 구성한 인증 서비스.

    Raises:
        HTTPException: 계정 인증이 설정되지 않았으면 503이 발생한다.
    """
    auth = getattr(request.app.state, "auth", None)
    if auth is None:
        raise auth_error(
            503, "AUTH_DISABLED", "서버에 계정 인증이 설정되지 않았습니다."
        )
    return auth
