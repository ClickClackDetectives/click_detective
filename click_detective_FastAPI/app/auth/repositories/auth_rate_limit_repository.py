"""계정과 요청 출처별 인증 시도를 PostgreSQL에서 제한한다."""

import hmac
from datetime import UTC, datetime
from secrets import randbelow

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from app.auth.repositories.auth_schema import AttemptBucket
from app.auth.services.auth_errors import auth_error

WINDOW_SECONDS = 300


def reserve_attempt(db, bucket_key, window_number, limit):
    """정해진 구간에서 인증 시도 횟수를 한 번 증가시킨다.

    Args:
        db: 현재 인증 ORM 세션.
        bucket_key: 이메일 또는 연결 주소의 HMAC.
        window_number: 현재 시간 구간 번호.
        limit: 현재 구간에서 허용하는 최대 시도 수.

    Returns:
        bool: 시도를 기록했으면 참, 상한에 도달했으면 거짓.
    """
    statement = insert(AttemptBucket).values(
        bucket_key=bucket_key, window_number=window_number, attempts=1
    )
    statement = statement.on_conflict_do_update(
        index_elements=[AttemptBucket.bucket_key, AttemptBucket.window_number],
        set_={"attempts": AttemptBucket.attempts + 1},
        where=AttemptBucket.attempts < limit,
    ).returning(AttemptBucket.attempts)
    return db.scalar(statement) is not None


def check_attempt(repository, key, action, email, peer):
    """고비용 비밀번호 처리 전에 다중 인스턴스의 사용량을 합산한다.

    Args:
        repository: PostgreSQL 인증 저장소.
        key: 이메일과 출처를 가리는 HMAC 비밀 키.
        action: signup 또는 login.
        email: 정규화한 계정 조회 키.
        peer: 인증 요청이 들어온 연결 상대 주소.

    Returns:
        None: 허용된 요청만 진행하며 제한 초과 시 HTTP 오류를 낸다.
    """
    peer_limit = 120 if action == "login" else 30
    account_limit = 8 if action == "login" else 4
    window_number = int(datetime.now(UTC).timestamp()) // WINDOW_SECONDS
    peer_key = hmac.digest(key, f"{action}:peer:{peer}".encode(), "sha256")
    email_key = hmac.digest(key, f"{action}:email:{email}".encode(), "sha256")
    with repository.connection() as db:
        if randbelow(128) == 0:
            db.execute(
                delete(AttemptBucket).where(
                    AttemptBucket.window_number < window_number - 1
                )
            )
        accepted = reserve_attempt(db, peer_key, window_number, peer_limit)
        if accepted:
            accepted = reserve_attempt(db, email_key, window_number, account_limit)
    if not accepted:
        raise auth_error(429, "AUTH_RATE_LIMITED", "잠시 후 다시 시도하세요.")
