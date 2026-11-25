"""PostgreSQL 계정과 세션을 SQLAlchemy ORM으로 저장한다."""

from contextlib import contextmanager

import psycopg
from sqlalchemy import create_engine, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import OperationalError, TimeoutError
from sqlalchemy.orm import sessionmaker

from .errors import auth_error, require_expected_account
from .schema import AuthBase, LoginSession, RefreshToken, User


class AuthRepository:
    """계정과 세션의 연결 풀 및 짧은 ORM 트랜잭션을 관리한다.

    Args:
        dsn: PostgreSQL 연결 문자열.

    Returns:
        AuthRepository: 인증 계정 및 세션의 영속 저장소.
    """

    def __init__(self, dsn):
        """연결 풀을 열고 초기 스키마를 준비한다.

        Args:
            dsn: PostgreSQL 연결 문자열.

        Returns:
            None: 반환값 없음.
        """

        def connect():
            """PostgreSQL 연결을 인증용 ORM 풀에 제공한다.

            Args:
                없음.

            Returns:
                psycopg.Connection: 비밀 연결 문자열로 연 PostgreSQL 연결.
            """
            return psycopg.connect(dsn, connect_timeout=5)

        self.engine = create_engine(
            "postgresql+psycopg://",
            creator=connect,
            pool_size=8,
            max_overflow=0,
            pool_timeout=5,
            pool_pre_ping=True,
            hide_parameters=True,
        )
        self.sessions = sessionmaker(self.engine)
        try:
            with self.connection() as db:
                db.scalar(select(func.pg_advisory_xact_lock(492821260)))
                AuthBase.metadata.create_all(db.connection())
        except BaseException:
            self.close()
            raise

    def close(self):
        """사용 중인 PostgreSQL 연결 풀을 닫는다.

        Args:
            없음.

        Returns:
            None: 반환값 없음.
        """
        self.engine.dispose()

    @contextmanager
    def connection(self):
        """ORM 세션과 트랜잭션을 제공하고 연결 장애를 API 오류로 바꾼다.

        Args:
            없음.

        Returns:
            ContextManager: 성공 시 확정하고 예외 시 롤백하는 ORM 세션.
        """
        try:
            with self.sessions.begin() as db:
                yield db
        except (OperationalError, TimeoutError) as error:
            raise auth_error(
                503, "AUTH_UNAVAILABLE", "인증 저장소에 연결할 수 없습니다."
            ) from error

    def insert_user(self, user):
        """고유 이메일을 기준으로 신규 계정을 등록한다.

        Args:
            user: 허용된 계정 등록 필드.

        Returns:
            bool: 계정을 삽입했으면 참, 기존 이메일이면 거짓.
        """
        statement = insert(User).values(**user.model_dump(), status="active")
        statement = statement.on_conflict_do_nothing(
            index_elements=[User.email_lookup]
        ).returning(User.id)
        with self.connection() as db:
            return db.scalar(statement) is not None

    def lookup(self, query):
        """활성 계정의 비밀번호 검증 정보를 조회한다.

        Args:
            query: 정규화한 이메일 키 입력.

        Returns:
            Mapping | None: 계정의 내부 등록 정보 또는 활성 계정 없음.
        """
        statement = select(User.id, User.email, User.password_hash).where(
            User.email_lookup == query.email_lookup, User.status == "active"
        )
        with self.connection() as db:
            return db.execute(statement).mappings().one_or_none()

    def insert_session(self, session, password_hash, upgraded_hash):
        """검증한 계정의 세션과 최초 갱신 토큰을 함께 저장한다.

        Args:
            session: 세션과 첫 갱신 토큰의 저장 입력.
            password_hash: 로그인에서 검증한 비밀번호 해시.
            upgraded_hash: 현재 정책으로 갱신할 해시 또는 None.

        Returns:
            bool: 활성 계정의 검증한 자격 증명이 유효해서 저장했으면 참.
        """
        statement = (
            select(User)
            .where(User.id == session.user_id, User.status == "active")
            .with_for_update()
        )
        with self.connection() as db:
            user = db.scalar(statement)
            if user is None or user.password_hash != password_hash:
                return False
            if upgraded_hash:
                user.password_hash = upgraded_hash
            db.add(
                LoginSession(
                    id=session.id,
                    user_id=session.user_id,
                    created_at=session.issued_at,
                    expires_at=session.expires_at,
                )
            )
            db.flush()
            db.add(
                RefreshToken(
                    token_hash=session.refresh_hash,
                    session_id=session.id,
                    issued_at=session.issued_at,
                    expires_at=session.expires_at,
                )
            )
            return True

    def active_user(self, user_id, session_id):
        """접근 JWT와 계정이 아직 유효한 세션에 속하는지 확인한다.

        Args:
            user_id: 검증한 JWT의 계정 UUID.
            session_id: 검증한 JWT의 세션 UUID.

        Returns:
            Mapping | None: 활성 계정 요약 또는 유효한 세션 없음.
        """
        statement = (
            select(User.id, User.email)
            .join(LoginSession, LoginSession.user_id == User.id)
            .where(
                User.id == user_id,
                LoginSession.id == session_id,
                User.status == "active",
                LoginSession.revoked_at.is_(None),
                LoginSession.expires_at > func.clock_timestamp(),
            )
        )
        with self.connection() as db:
            return db.execute(statement).mappings().one_or_none()

    def revoke(self, refresh_hash, identity, expected_user):
        """확인된 토큰이 가리키는 세션을 폐기한다.

        Args:
            refresh_hash: 갱신 토큰 해시 또는 None.
            identity: 갱신 토큰을 찾을 수 없을 때 사용할 계정 및 세션 UUID 쌍.
            expected_user: 로그아웃을 요청한 화면의 계정 ID 또는 None.

        Returns:
            None: 대상 세션이 없거나 이전에 폐기됐어도 성공한다.
        """
        with self.connection() as db:
            if refresh_hash is not None:
                statement = (
                    select(LoginSession.user_id, LoginSession.id)
                    .join(RefreshToken, RefreshToken.session_id == LoginSession.id)
                    .where(RefreshToken.token_hash == refresh_hash)
                )
                session = db.execute(statement).one_or_none()
                if session is not None:
                    identity = session.user_id, session.id
            if identity is not None:
                user_id, session_id = identity
                require_expected_account(user_id, expected_user)
                statement = (
                    update(LoginSession)
                    .where(
                        LoginSession.revoked_at.is_(None),
                        LoginSession.user_id == user_id,
                        LoginSession.id == session_id,
                    )
                    .values(revoked_at=func.clock_timestamp())
                )
                db.execute(statement)
