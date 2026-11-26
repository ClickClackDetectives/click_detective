"""계정 API와 DB 쓰기 계약을 구분한다."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class Credentials(BaseModel):
    """가입 또는 로그인에 필요한 자격 증명을 검증한다.

    Args:
        email: 이메일 주소.
        password: 비밀번호 원문이며 입력 크기를 제한한다.

    Returns:
        Credentials: 계정 API의 입력 DTO.
    """

    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=1, max_length=254)
    password: SecretStr = Field(min_length=1, max_length=256)


class DeleteAccount(BaseModel):
    """계정 탈퇴 확인에 필요한 현재 비밀번호를 받는다.

    Args:
        password: 본인이 입력한 현재 비밀번호 원문.

    Returns:
        DeleteAccount: 비밀번호 재확인을 위한 탈퇴 요청 DTO.
    """

    model_config = ConfigDict(extra="forbid")
    password: SecretStr = Field(min_length=1, max_length=256)


class Account(BaseModel):
    """공개 가능한 계정 필드를 정의한다.

    Args:
        id: 계정 UUID.
        email: 정규화한 이메일.

    Returns:
        Account: 비밀번호와 토큰을 제외한 계정 정보.
    """

    id: str
    email: str


class TokenPair(BaseModel):
    """서버 중계에서만 사용하는 인증 토큰 응답을 정의한다.

    Args:
        user: 공개 계정 정보.
        access_token: 서명한 접근 토큰 원문.
        refresh_token: 불투명 갱신 토큰 원문.
        access_expires_at: 접근 토큰 만료 UTC 시각.
        refresh_expires_at: 세션과 갱신 토큰의 만료 UTC 시각.

    Returns:
        TokenPair: Next.js 서버에서 쿠키로 옮길 토큰 계약.
    """

    user: Account
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


class UserInsert(BaseModel):
    """사용자 등록에 허용된 PostgreSQL 입력을 묶는다.

    Args:
        id: 생성할 계정 UUID.
        email: 표시용 이메일.
        email_lookup: 중복 확인에 사용할 정규화 키.
        password_hash: Argon2id 해시.
        created_at: 계정 생성 UTC 시각.

    Returns:
        UserInsert: 활성 계정을 등록할 때 사용할 입력.
    """

    id: UUID
    email: str
    email_lookup: str
    password_hash: str
    created_at: datetime


class LoginLookup(BaseModel):
    """로그인용 계정 조회 키를 보관한다.

    Args:
        email_lookup: 정규화한 이메일의 대소문자 무시 조회 키.

    Returns:
        LoginLookup: 로그인 계정 조회 입력.
    """

    email_lookup: str


class SessionInsert(BaseModel):
    """로그인 세션 및 최초 갱신 토큰의 저장 필드를 묶는다.

    Args:
        id: 로그인 세션 UUID.
        user_id: 비밀번호 검증을 통과한 계정 UUID.
        issued_at: 첫 로그인 UTC 시각.
        expires_at: 로그인 세션의 고정 만료 UTC 시각.
        refresh_hash: 최초 갱신 토큰의 32바이트 SHA-256 해시.

    Returns:
        SessionInsert: 한 트랜잭션으로 등록할 세션 입력.
    """

    id: UUID
    user_id: UUID
    issued_at: datetime
    expires_at: datetime
    refresh_hash: bytes


class UserInsertBuilder:
    """가입 서비스의 처리 결과를 사용자 등록 입력으로 조립한다.

    Args:
        없음.

    Returns:
        UserInsertBuilder: 호출별 등록 입력을 만드는 빌더.
    """

    @staticmethod
    def build(email, password_hash, now):
        """정규화한 이메일과 해시를 등록 입력으로 옮긴다.

        Args:
            email: 정규화한 이메일.
            password_hash: Argon2id 해시.
            now: 계정 생성 UTC 시각.

        Returns:
            UserInsert: 활성 사용자 등록 입력.
        """
        return UserInsert(
            id=uuid4(),
            email=email,
            email_lookup=email.casefold(),
            password_hash=password_hash,
            created_at=now,
        )


class LoginLookupBuilder:
    """이메일의 로그인 조회 키를 만드는 빌더다.

    Args:
        없음.

    Returns:
        LoginLookupBuilder: 정규화한 이메일을 조회 모델로 옮기는 빌더.
    """

    @staticmethod
    def build(email):
        """정규화한 이메일에서 대소문자를 무시하는 조회 키를 만든다.

        Args:
            email: 정규화한 이메일.

        Returns:
            LoginLookup: 로그인 계정 조회 입력.
        """
        return LoginLookup(email_lookup=email.casefold())


class SessionInsertBuilder:
    """서버에서 발급한 세션 정보를 저장 입력으로 조립한다.

    Args:
        없음.

    Returns:
        SessionInsertBuilder: 세션과 최초 갱신 토큰의 저장 모델을 만드는 빌더.
    """

    @staticmethod
    def build(user_id, issued_at, expires_at, refresh_hash):
        """첫 로그인 세션을 새 UUID로 구성한다.

        Args:
            user_id: 비밀번호를 검증한 사용자 UUID.
            issued_at: 최초 로그인 UTC 시각.
            expires_at: 최초 로그인에 고정된 종료 UTC 시각.
            refresh_hash: 최초 갱신 토큰의 SHA-256 해시.

        Returns:
            SessionInsert: 트랜잭션 등록 계약.
        """
        return SessionInsert(
            id=uuid4(),
            user_id=user_id,
            issued_at=issued_at,
            expires_at=expires_at,
            refresh_hash=refresh_hash,
        )
