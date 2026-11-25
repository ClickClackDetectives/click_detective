"""접근 토큰 JWT와 갱신 토큰의 해시 정책을 제공한다."""

import hashlib
from datetime import timedelta
from uuid import UUID

import jwt

from .errors import auth_error

ISSUER = "click-detective-auth"
AUDIENCE = "click-detective-api"


def token_hash(token):
    """서버에서 발급한 갱신 토큰을 저장용 해시로 바꾼다.

    Args:
        token: 갱신 토큰 원문.

    Returns:
        bytes: 32바이트 SHA-256 해시.
    """
    return hashlib.sha256(token.encode()).digest()


def issue_pair(key, user, session_id, now, expires_at, refresh_token):
    """접근 토큰과 갱신 토큰을 세션의 고정 만료 범위에 맞춰 반환한다.

    Args:
        key: JWT 서명 키.
        user: 계정 ID와 이메일을 담은 공개 요약.
        session_id: 로그인 세션 UUID.
        now: 토큰 발급 UTC 시각.
        expires_at: 최초 로그인에 고정된 세션 종료 UTC 시각.
        refresh_token: 새로 발급한 갱신 토큰 원문.

    Returns:
        dict: 사용자, 두 토큰과 각 만료 시각을 담은 서버용 응답.
    """
    access_expires_at = min(now + timedelta(hours=2), expires_at).replace(microsecond=0)
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": user["id"],
        "sid": str(session_id),
        "purpose": "access",
        "iat": now,
        "exp": access_expires_at,
    }
    return {
        "user": user,
        "access_token": jwt.encode(claims, key, algorithm="HS256"),
        "refresh_token": refresh_token,
        "access_expires_at": access_expires_at,
        "refresh_expires_at": expires_at,
    }


def access_identity(key, token, *, allow_expired=False):
    """서명과 용도를 검사하고 JWT의 계정 및 세션 ID를 꺼낸다.

    Args:
        key: JWT 검증 키.
        token: 접근 토큰 원문.
        allow_expired: 로그아웃에서만 만료된 서명 토큰의 세션 참조를 허용한다.

    Returns:
        tuple[UUID, UUID]: 인증된 계정 ID와 로그인 세션 ID.

    Raises:
        HTTPException: 토큰이 비어 있거나, 유효하지 않거나, 만료되면 발생한다.
    """
    if not token:
        raise auth_error(401, "ACCESS_TOKEN_MISSING", "로그인이 필요합니다.")
    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=["HS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={
                "require": ["iss", "aud", "sub", "sid", "purpose", "iat", "exp"],
                "verify_exp": not allow_expired,
            },
        )
        if claims["purpose"] == "access":
            return UUID(claims["sub"]), UUID(claims["sid"])
    except jwt.ExpiredSignatureError as error:
        raise auth_error(
            401, "ACCESS_TOKEN_EXPIRED", "접근 토큰이 만료되었습니다."
        ) from error
    except (jwt.InvalidTokenError, TypeError, ValueError, AttributeError) as error:
        raise auth_error(
            401, "ACCESS_TOKEN_INVALID", "접근 토큰이 유효하지 않습니다."
        ) from error
    raise auth_error(401, "ACCESS_TOKEN_INVALID", "접근 토큰이 유효하지 않습니다.")
