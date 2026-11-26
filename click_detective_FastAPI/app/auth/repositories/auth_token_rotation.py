"""세션 잠금으로 갱신 토큰 교체와 재사용 감지를 직렬화한다."""

from datetime import UTC, datetime

from sqlalchemy import select

from app.auth.repositories.auth_schema import LoginSession, RefreshToken, User
from app.auth.services.auth_errors import auth_error, require_expected_account


def rotate(repository, previous_hash, next_hash, expected_user):
    """활성 세션에 새 갱신 토큰을 기록한다.

    Args:
        repository: PostgreSQL 인증 저장소.
        previous_hash: 요청으로 받은 갱신 토큰의 해시.
        next_hash: 새로 발급할 갱신 토큰의 해시.
        expected_user: 갱신 요청을 발생시킨 화면의 계정 ID 또는 None.

    Returns:
        tuple[dict, datetime]: 계정 및 세션 정보와 갱신 시각.

    Raises:
        HTTPException: 갱신 토큰이 없거나 세션을 사용할 수 없다.
    """
    token_session = select(RefreshToken.session_id).where(
        RefreshToken.token_hash == previous_hash
    )
    statement = (
        select(LoginSession, User.id, User.email, User.status)
        .join(User, LoginSession.user_id == User.id)
        .where(LoginSession.id == token_session.scalar_subquery())
        .with_for_update(of=LoginSession)
    )
    with repository.connection() as db:
        row = db.execute(statement).one_or_none()
        if row is None:
            raise auth_error(401, "REFRESH_TOKEN_INVALID", "다시 로그인하세요.")
        login, user_id, email, status = row
        require_expected_account(user_id, expected_user)
        now = datetime.now(UTC)
        if (
            login.revoked_at is not None
            or login.expires_at <= now
            or status != "active"
        ):
            raise auth_error(401, "SESSION_REVOKED", "다시 로그인하세요.")
        # 잠금 대기 중 선행 요청이 토큰을 교체할 수 있어 잠금 후 다시 읽는다.
        previous = db.get(RefreshToken, previous_hash)
        replayed = previous.used_at is not None
        if replayed:
            login.revoked_at = now
        else:
            if previous.expires_at <= now:
                raise auth_error(401, "REFRESH_TOKEN_INVALID", "다시 로그인하세요.")
            previous.used_at = now
            db.flush()
            db.add(
                RefreshToken(
                    token_hash=next_hash,
                    session_id=login.id,
                    issued_at=now,
                    expires_at=login.expires_at,
                )
            )
        session = {
            "id": user_id,
            "email": email,
            "session_id": login.id,
            "expires_at": login.expires_at,
        }
    if replayed:
        raise auth_error(401, "SESSION_REVOKED", "다시 로그인하세요.")
    return session, now
