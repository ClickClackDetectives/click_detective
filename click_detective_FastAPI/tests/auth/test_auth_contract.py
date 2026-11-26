"""계정 API와 토큰 만료, 회전 및 폐기 계약을 검증한다."""

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi import FastAPI, HTTPException, Request
from psycopg import connect, sql
from psycopg.conninfo import make_conninfo
from sqlalchemy import func, update

from app.auth.controllers.auth_request_context import current_user
from app.auth.repositories.auth_schema import DeletionJob
from app.auth.services.auth_deletion_service import process_one
from app.auth.services.auth_service import AuthService
from app.auth.services.auth_tokens import access_identity, issue_pair

EMAIL = "detective@example.com"
PASSWORD = "Detective1!"


@pytest.fixture
def auth():
    """임시 PostgreSQL 스키마에서 실제 인증 서비스를 준비한다.

    Args:
        없음.

    Returns:
        Iterator[AuthService]: 테스트용 서비스이며 종료 시 스키마를 삭제한다.
    """
    dsn = os.getenv("CLICK_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("PostgreSQL 통합 설정이 필요합니다.")
    schema_name = f"auth_test_{uuid4().hex}"
    schema = sql.Identifier(schema_name)
    with connect(dsn, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE SCHEMA {}").format(schema))
        try:
            isolated_dsn = make_conninfo(dsn, options=f"-c search_path={schema_name}")
            service = AuthService(isolated_dsn, "a" * 48)
            try:
                yield service
            finally:
                service.close()
        finally:
            admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(schema))


def test_disabled_auth_fails_with_explicit_code():
    """인증 미설정 오류가 사용자 인증 실패와 구별되는지 확인한다.

    Args:
        없음.

    Returns:
        None: 미설정 서비스의 오류 계약을 검증한다.
    """
    app = FastAPI()
    app.state.auth = None
    request = Request({"type": "http", "app": app, "headers": []})
    with pytest.raises(HTTPException) as error:
        current_user(request)
    assert error.value.status_code == 503
    assert error.value.detail["code"] == "AUTH_DISABLED"


def test_concurrent_refresh_rotates_once_and_revokes_on_replay(auth):
    """동시 갱신에서는 한 요청만 회전하고 재사용이 세션을 폐기한다.

    Args:
        auth: 독립 PostgreSQL 스키마를 사용하는 인증 서비스.

    Returns:
        None: 단일 토큰 발급, 고정 만료와 재사용 후 접근 거부를 검증한다.
    """
    user = auth.signup(EMAIL, PASSWORD)
    initial = auth.login(EMAIL, PASSWORD)
    assert auth.me(initial["access_token"]) == user
    barrier = Barrier(2, timeout=10)

    def attempt_refresh():
        """동일 갱신 토큰으로 동시 회전 경쟁에 참여한다.

        Args:
            없음.

        Returns:
            dict | str: 새 토큰 정보 또는 API 인증 오류 코드.
        """
        barrier.wait()
        try:
            return auth.refresh(initial["refresh_token"])
        except HTTPException as error:
            return error.detail["code"]

    with ThreadPoolExecutor(max_workers=2) as pool:
        pending = [pool.submit(attempt_refresh) for _ in range(2)]
        results = [future.result(timeout=10) for future in pending]
    pairs = [result for result in results if isinstance(result, dict)]
    assert len(pairs) == 1
    assert "SESSION_REVOKED" in results
    rotated = pairs[0]
    assert rotated["refresh_expires_at"] == initial["refresh_expires_at"]
    assert rotated["refresh_token"] != initial["refresh_token"]
    with pytest.raises(HTTPException) as revoked:
        auth.me(rotated["access_token"])
    assert revoked.value.detail["code"] == "SESSION_REVOKED"


def test_refresh_and_logout_reject_a_different_expected_account(auth):
    """이전 탭의 요청은 브라우저에서 바뀐 로그인 계정에 영향을 주지 않는다.

    Args:
        auth: 독립 PostgreSQL 스키마를 사용하는 인증 서비스.

    Returns:
        None: 잘못된 계정 ID를 가진 요청의 부작용 부재를 확인한다.
    """
    user = auth.signup(EMAIL, PASSWORD)
    initial = auth.login(EMAIL, PASSWORD)
    foreign_id = str(uuid4())
    with pytest.raises(HTTPException) as refresh_error:
        auth.refresh(initial["refresh_token"], expected_user=foreign_id)
    assert refresh_error.value.detail["code"] == "ACCOUNT_CHANGED"
    with pytest.raises(HTTPException) as logout_error:
        auth.logout(initial["refresh_token"], "", expected_user=foreign_id)
    assert logout_error.value.detail["code"] == "ACCOUNT_CHANGED"
    rotated = auth.refresh(initial["refresh_token"], expected_user=user["id"])
    assert auth.me(rotated["access_token"]) == user


def test_login_rate_limit_is_shared_by_normalized_email(auth):
    """같은 이메일의 대소문자나 연결 주소를 바꿔도 할당량을 공유한다.

    Args:
        auth: 독립 PostgreSQL 스키마를 사용하는 인증 서비스.

    Returns:
        None: 이메일 단위의 공통 한도와 다른 계정의 독립 할당량을 검증한다.
    """
    for _ in range(8):
        auth.throttle("login", EMAIL, "192.0.2.10")
    with pytest.raises(HTTPException) as limited:
        auth.throttle("login", EMAIL.upper(), "192.0.2.11")
    assert limited.value.status_code == 429
    auth.throttle("login", "other@example.com", "192.0.2.10")


def test_account_deletion_revokes_sessions_and_completes_after_retry(auth):
    """탈퇴와 정리 실패가 기존 세션을 되살리거나 계정을 일찍 삭제하지 않는다.

    Args:
        auth: 독립 PostgreSQL 스키마를 사용하는 인증 서비스.

    Returns:
        None: 즉시 폐기, 최초 실행 지연, 실패 후 재시도와 완료를 확인한다.
    """
    user = auth.signup(EMAIL, PASSWORD)
    session = auth.login(EMAIL, PASSWORD)
    auth.delete(user["id"], PASSWORD)
    with pytest.raises(HTTPException) as revoked:
        auth.me(session["access_token"])
    assert revoked.value.detail["code"] == "SESSION_REVOKED"

    removed = []
    assert not process_one(auth.repository, removed.append)
    release_deletion_job(auth)

    def fail_delete(user_id):
        """수사 저장소의 일시적 장애를 모의한다.

        Args:
            user_id: 처리할 계정 UUID.

        Returns:
            None: 작업 실패를 나타내는 예외를 낸다.
        """
        raise RuntimeError(f"임시 저장소 장애: {user_id}")

    with pytest.raises(RuntimeError, match="임시 저장소 장애"):
        process_one(auth.repository, fail_delete)
    assert not process_one(auth.repository, removed.append)
    with pytest.raises(HTTPException) as duplicate:
        auth.signup(EMAIL, PASSWORD)
    assert duplicate.value.detail["code"] == "EMAIL_EXISTS"

    release_deletion_job(auth)
    assert process_one(auth.repository, removed.append)
    assert removed == [user["id"]]
    assert auth.signup(EMAIL, PASSWORD)["id"] != user["id"]
    assert not process_one(auth.repository, removed.append)


def release_deletion_job(auth):
    """실제 지연 시간을 기다리지 않고 테스트 작업의 정리 시각을 도달시킨다.

    Args:
        auth: 독립 PostgreSQL 스키마를 사용하는 인증 서비스.

    Returns:
        None: 테스트 스키마의 작업 실행 시각이 현재로 이동한다.
    """
    with auth.repository.connection() as db:
        db.execute(update(DeletionJob).values(next_attempt_at=func.clock_timestamp()))


def test_expired_access_token_cannot_authenticate():
    """접근 토큰의 서명이 올바르더라도 만료되면 요청을 거부한다.

    Args:
        없음.

    Returns:
        None: JWT 만료 오류와 로그아웃용 세션 참조를 검증한다.
    """
    user_id = uuid4()
    session_id = uuid4()
    key = "test-secret-" * 4
    now = datetime.now(UTC) - timedelta(hours=3)
    tokens = issue_pair(
        key,
        {"id": str(user_id), "email": EMAIL},
        session_id,
        now,
        now + timedelta(days=7),
        "placeholder",
    )
    with pytest.raises(HTTPException) as error:
        access_identity(key, tokens["access_token"])
    assert error.value.detail["code"] == "ACCESS_TOKEN_EXPIRED"
    assert access_identity(key, tokens["access_token"], allow_expired=True) == (
        user_id,
        session_id,
    )
