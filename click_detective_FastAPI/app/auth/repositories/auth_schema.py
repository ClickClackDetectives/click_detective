"""PostgreSQL 인증 테이블을 SQLAlchemy 모델로 선언한다."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    Text,
    column,
    func,
    literal_column,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class AuthBase(DeclarativeBase):
    """인증 테이블의 공통 SQLAlchemy 메타데이터를 제공한다.

    Args:
        없음.

    Returns:
        AuthBase: PostgreSQL 인증 모델의 선언 기반.
    """


class User(AuthBase):
    """정규화된 이메일을 가진 계정과 비밀번호 해시를 저장한다.

    Args:
        **kwargs: 등록 시 매핑할 계정 열의 값.

    Returns:
        User: 등록된 계정 행을 나타내는 인스턴스.
    """

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(column("status").in_(("active", "deletion_pending"))),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(Text)
    email_lookup: Mapped[str] = mapped_column(Text, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class LoginSession(AuthBase):
    """계정에 속한 로그인 세션과 폐기 상태를 저장한다.

    Args:
        **kwargs: 세션의 식별자, 계정과 수명 정보.

    Returns:
        LoginSession: 로그인 세션 행을 나타내는 인스턴스.
    """

    __tablename__ = "auth_sessions"
    __table_args__ = (
        CheckConstraint(column("expires_at") > column("created_at")),
        Index("auth_sessions_user_idx", "user_id"),
        Index("auth_sessions_expiry_idx", "expires_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RefreshToken(AuthBase):
    """세션의 갱신 토큰 해시와 회전 상태를 저장한다.

    Args:
        **kwargs: 토큰 해시, 세션 참조와 시각 필드.

    Returns:
        RefreshToken: 원문을 제외한 갱신 토큰 행을 나타내는 인스턴스.
    """

    __tablename__ = "auth_refresh_tokens"
    __table_args__ = (
        CheckConstraint(func.octet_length(column("token_hash")) == 32),
        CheckConstraint(column("expires_at") > column("issued_at")),
        CheckConstraint(column("used_at") >= column("issued_at")),
        Index("auth_refresh_tokens_session_idx", "session_id"),
        Index(
            "auth_refresh_tokens_active_idx",
            "session_id",
            unique=True,
            postgresql_where=column("used_at").is_(None),
        ),
    )

    token_hash: Mapped[bytes] = mapped_column(LargeBinary, primary_key=True)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("auth_sessions.id"))
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AttemptBucket(AuthBase):
    """이메일 또는 연결 출처별 인증 시도 횟수를 저장한다.

    Args:
        **kwargs: 키 해시, 시간 구간과 시도 횟수.

    Returns:
        AttemptBucket: 분산 인증 요청의 횟수 집계 행을 나타내는 인스턴스.
    """

    __tablename__ = "auth_attempt_buckets"
    __table_args__ = (
        CheckConstraint(column("attempts") > 0),
        Index("auth_attempt_buckets_window_idx", "window_number"),
    )

    bucket_key: Mapped[bytes] = mapped_column(LargeBinary, primary_key=True)
    window_number: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    attempts: Mapped[int]


class DeletionJob(AuthBase):
    """계정 삭제 작업의 예약과 처리 상태를 저장한다.

    Args:
        **kwargs: 삭제 작업 및 계정 식별자와 예약 정보.

    Returns:
        DeletionJob: 작업 실행권과 완료 상태를 포함한 인스턴스.
    """

    __tablename__ = "account_deletion_jobs"
    __table_args__ = (
        CheckConstraint(column("status").in_(("pending", "running", "completed"))),
        CheckConstraint(column("attempt_count") >= 0),
        Index("deletion_jobs_status_idx", "status", "next_attempt_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(unique=True)
    status: Mapped[str] = mapped_column(Text, server_default="pending")
    attempt_count: Mapped[int] = mapped_column(server_default=literal_column("0"))
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
