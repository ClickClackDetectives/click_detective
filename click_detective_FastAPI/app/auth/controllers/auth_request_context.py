"""서버 중계 요청의 계정 인증 문맥을 읽는다."""

from fastapi import Request

from app.auth.providers.auth_provider import get_auth_service
from app.auth.services.auth_errors import require_expected_account


def current_user(request: Request):
    """서버 중계가 제공한 접근 토큰과 기대 계정을 검증한다.

    Args:
        request: 서버 중계의 인증 헤더가 들어있는 요청.

    Returns:
        dict: 인증된 계정 ID와 이메일.
    """
    token = request.headers.get("X-Access-Token", "")
    user = get_auth_service(request).me(token)
    expected_user = request.headers.get("X-Expected-User-Id")
    require_expected_account(user["id"], expected_user)
    return user
