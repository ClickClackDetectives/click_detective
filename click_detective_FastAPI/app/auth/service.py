"""가입과 로그인 및 토큰 수명을 관리한다."""

import re
import secrets
from datetime import UTC, datetime, timedelta
from string import punctuation

from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException
from pwdlib import PasswordHash

from .contracts import LoginLookupBuilder, SessionInsertBuilder, UserInsertBuilder
from .deletion import verify_deletion
from .errors import auth_error
from .rate_limit import check_attempt
from .repository import AuthRepository
from .rotation import rotate
from .tokens import access_identity, issue_pair, token_hash


def public_user(row):
    """DB에서 읽은 내부 행을 공개 계정 정보로 제한한다.

    Args:
        row: 문자열로 변환할 계정 ID와 이메일을 포함한 저장 행.

    Returns:
        dict: 공개 계정 ID와 이메일.
    """
    return {"id": str(row["id"]), "email": row["email"]}


def login_failed():
    """가입 여부와 비밀번호 오류를 공통 메시지로 나타낸다.

    Args:
        없음.

    Returns:
        HTTPException: 잘못된 로그인 요청의 오류.
    """
    return auth_error(401, "LOGIN_FAILED", "이메일 또는 비밀번호를 확인하세요.")


class AuthService:
    """계정과 세션 유스케이스를 제공하고 저장소 수명을 관리한다.

    Args:
        postgres_dsn: 인증 PostgreSQL 연결 문자열.
        jwt_secret: 32바이트 이상인 HS256 서명 키.

    Returns:
        AuthService: FastAPI 앱이 공유하는 계정 인증 서비스.
    """

    def __init__(self, postgres_dsn, jwt_secret):
        """인증 저장소와 비밀번호 해시 정책을 준비한다.

        Args:
            postgres_dsn: 인증 PostgreSQL 연결 문자열.
            jwt_secret: 32바이트 이상인 HS256 서명 키.

        Returns:
            None: 반환값 없음.
        """
        if len(jwt_secret.encode()) < 32:
            raise ValueError("인증 JWT 서명 키는 32바이트 이상이어야 합니다.")
        self.key = jwt_secret
        self.passwords = PasswordHash.recommended()
        self.dummy_hash = self.passwords.hash(secrets.token_urlsafe(32))
        self.repository = AuthRepository(postgres_dsn)

    def close(self):
        """인증 PostgreSQL 연결 풀을 닫는다.

        Args:
            없음.

        Returns:
            None: 반환값 없음.
        """
        self.repository.close()

    def throttle(self, action, email, peer):
        """가입 또는 로그인에서 이메일과 연결 상대의 사용량을 제한한다.

        Args:
            action: 가입 또는 로그인 작업 이름.
            email: 브라우저가 입력한 계정 주소.
            peer: 로그인 요청을 전달한 연결 상대 주소.

        Returns:
            None: 할당량 안에서 요청을 진행한다.
        """
        email = email.strip()
        try:
            email = validate_email(email, check_deliverability=False).normalized
        except EmailNotValidError:
            pass
        check_attempt(
            self.repository, self.key.encode(), action, email.casefold(), peer
        )

    def signup(self, email, password):
        """이메일과 비밀번호 정책을 검사하고 새 활성 계정을 등록한다.

        Args:
            email: 대소문자 무시 중복 확인을 적용할 주소.
            password: 영문, 숫자, 특수문자를 각각 포함한 8~16자 비밀번호 원문.

        Returns:
            dict: 공개 계정 ID와 이메일.
        """
        try:
            email = validate_email(email.strip(), check_deliverability=False).normalized
        except EmailNotValidError as error:
            raise auth_error(
                422, "INVALID_EMAIL", "이메일 주소를 확인하세요."
            ) from error
        valid_length = 8 <= len(password) <= 16
        has_letter = re.search(r"[A-Za-z]", password) is not None
        has_digit = re.search(r"[0-9]", password) is not None
        has_special = any(char in punctuation for char in password)
        if not all((valid_length, has_letter, has_digit, has_special)):
            raise auth_error(
                422,
                "INVALID_PASSWORD",
                "비밀번호는 8~16자로 입력하고 영문, 숫자, 특수문자를 각각 포함하세요.",
            )
        user = UserInsertBuilder.build(
            email, self.passwords.hash(password), datetime.now(UTC)
        )
        if not self.repository.insert_user(user):
            raise auth_error(409, "EMAIL_EXISTS", "이미 사용 중인 이메일입니다.")
        return {"id": str(user.id), "email": user.email}

    def login(self, email, password):
        """등록 여부를 노출하지 않고 자격 증명을 확인하여 새 세션을 연다.

        Args:
            email: 등록한 이메일 주소.
            password: 확인할 비밀번호 원문.

        Returns:
            dict: 공개 계정, 접근 및 갱신 토큰, 각각의 만료 시각.
        """
        try:
            email = validate_email(email.strip(), check_deliverability=False).normalized
        except EmailNotValidError:
            user = None
        else:
            user = self.repository.lookup(LoginLookupBuilder.build(email))
        password_hash = self.dummy_hash if user is None else user["password_hash"]
        valid, upgraded = self.passwords.verify_and_update(password, password_hash)
        if user is None or not valid:
            raise login_failed()

        now = datetime.now(UTC)
        expires_at = now + timedelta(days=7)
        refresh_token = secrets.token_urlsafe(32)
        session = SessionInsertBuilder.build(
            user["id"], now, expires_at, token_hash(refresh_token)
        )
        if not self.repository.insert_session(session, password_hash, upgraded):
            raise login_failed()
        return issue_pair(
            self.key, public_user(user), session.id, now, expires_at, refresh_token
        )

    def me(self, access_token):
        """접근 JWT와 세션의 현재 유효성을 확인한다.

        Args:
            access_token: Next.js 서버가 보낸 접근 토큰 원문.

        Returns:
            dict: 접근 토큰의 공개 계정 ID와 이메일.
        """
        user_id, session_id = access_identity(self.key, access_token)
        user = self.repository.active_user(user_id, session_id)
        if user is None:
            raise auth_error(401, "SESSION_REVOKED", "다시 로그인하세요.")
        return public_user(user)

    def refresh(self, refresh_token, *, expected_user=None):
        """이전 갱신 토큰을 사용 처리하고 세션 만료 내의 토큰 쌍을 재발급한다.

        Args:
            refresh_token: 아직 사용되지 않은 현재 갱신 토큰 원문.
            expected_user: 갱신 요청을 발생시킨 화면의 계정 ID 또는 None.

        Returns:
            dict: 교체된 두 토큰과 공개 계정 및 만료 시각.
        """
        if not refresh_token:
            raise auth_error(401, "REFRESH_TOKEN_INVALID", "다시 로그인하세요.")
        new_token = secrets.token_urlsafe(32)
        session, now = rotate(
            self.repository,
            token_hash(refresh_token),
            token_hash(new_token),
            expected_user,
        )
        return issue_pair(
            self.key,
            public_user(session),
            session["session_id"],
            now,
            session["expires_at"],
            new_token,
        )

    def delete(self, user_id, password):
        """현재 비밀번호를 확인하고 계정 데이터 삭제를 예약한다.

        Args:
            user_id: 요청에서 인증한 사용자 UUID.
            password: 탈퇴 확인용 현재 비밀번호 원문.

        Returns:
            None: 계정 상태 변경, 모든 세션 폐기 및 작업 등록이 완료된다.
        """
        verify_deletion(self.repository, self.passwords, user_id, password)

    def logout(self, refresh_token, access_token, *, expected_user=None):
        """저장소가 응답한 뒤 현재 로그인 세션의 폐기를 완료한다.

        Args:
            refresh_token: 만료된 접근 토큰을 대신해 세션을 식별하는 갱신 토큰 원문.
            access_token: 갱신 쿠키가 없어도 세션을 식별할 수 있는 서명 토큰 원문.
            expected_user: 로그아웃 요청을 발생시킨 화면의 계정 ID 또는 None.

        Returns:
            None: 폐기할 세션이 없거나 이미 폐기된 경우도 정상 완료한다.
        """
        identity = None
        if access_token:
            try:
                identity = access_identity(self.key, access_token, allow_expired=True)
            except HTTPException:
                pass
        refresh_hash = token_hash(refresh_token) if refresh_token else None
        if refresh_hash is not None or identity is not None:
            self.repository.revoke(refresh_hash, identity, expected_user)
