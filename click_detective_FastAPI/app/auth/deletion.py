"""계정 탈퇴 요청과 저장소 정리 작업을 관리한다."""

from datetime import timedelta
from uuid import UUID, uuid4

from sqlalchemy import delete, func, select, update

from .errors import auth_error
from .schema import DeletionJob, LoginSession, RefreshToken, User

JOB_LEASE = timedelta(minutes=15)


def verify_deletion(repository, passwords, user_id, password):
    """현재 비밀번호를 확인하고 탈퇴 작업을 멱등하게 등록한다.

    Args:
        repository: PostgreSQL 인증 저장소.
        passwords: 비밀번호 해시 검증기.
        user_id: 접근 JWT로 확인한 계정 UUID.
        password: 탈퇴를 확인하는 현재 비밀번호 원문.

    Returns:
        None: 탈퇴 작업 등록과 활성 세션 폐기가 확정된다.
    """
    account_id = UUID(str(user_id))
    with repository.connection() as db:
        password_hash = db.scalar(
            select(User.password_hash).where(
                User.id == account_id, User.status == "active"
            )
        )
    if password_hash is None:
        raise auth_error(401, "SESSION_REVOKED", "다시 로그인하세요.")

    if not passwords.verify(password, password_hash):
        raise auth_error(403, "PASSWORD_MISMATCH", "비밀번호를 확인하세요.")
    with repository.connection() as db:
        mark_pending = (
            update(User)
            .where(
                User.id == account_id,
                User.password_hash == password_hash,
                User.status == "active",
            )
            .values(status="deletion_pending")
            .returning(User.id)
        )
        if db.scalar(mark_pending) is None:
            raise auth_error(401, "SESSION_REVOKED", "다시 로그인하세요.")
        now = db.scalar(select(func.clock_timestamp()))
        db.execute(
            update(LoginSession)
            .where(
                LoginSession.user_id == account_id, LoginSession.revoked_at.is_(None)
            )
            .values(revoked_at=now)
        )
        db.add(
            DeletionJob(
                id=uuid4(),
                user_id=account_id,
                created_at=now,
                next_attempt_at=now + JOB_LEASE,
            )
        )


def claim_job(repository):
    """대기 작업이나 임대 만료 작업 하나의 실행권을 가져온다.

    Args:
        repository: PostgreSQL 인증 저장소.

    Returns:
        dict | None: 작업 ID와 계정 UUID 및 실행권 번호, 또는 실행 가능한 작업 없음.
    """
    statement = (
        select(DeletionJob)
        .where(
            DeletionJob.status.in_(("pending", "running")),
            DeletionJob.next_attempt_at <= func.clock_timestamp(),
        )
        .order_by(DeletionJob.next_attempt_at, DeletionJob.id)
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    with repository.connection() as db:
        job = db.scalar(statement)
        if job is None:
            return None
        now = db.scalar(select(func.clock_timestamp()))
        job.status = "running"
        job.attempt_count += 1
        job.next_attempt_at = now + JOB_LEASE
        return {
            "id": job.id,
            "user_id": job.user_id,
            "attempt_count": job.attempt_count,
        }


def postpone_job(repository, job):
    """아직 자신이 보유한 작업만 다음 실행을 위해 대기 상태로 돌린다.

    Args:
        repository: PostgreSQL 인증 저장소.
        job: 실행권을 가져온 작업의 ID, 계정과 실행권 번호.

    Returns:
        None: 현재 실행권에 해당하는 작업의 다음 시도 시각을 저장한다.
    """
    delay_seconds = min(3600, 30 * (2 ** min(job["attempt_count"] - 1, 7)))
    with repository.connection() as db:
        now = db.scalar(select(func.clock_timestamp()))
        db.execute(
            update(DeletionJob)
            .where(
                DeletionJob.id == job["id"],
                DeletionJob.status == "running",
                DeletionJob.attempt_count == job["attempt_count"],
            )
            .values(
                status="pending",
                next_attempt_at=now + timedelta(seconds=delay_seconds),
            )
        )


def complete_job(repository, job):
    """현재 실행권을 확인하고 인증 데이터 및 작업 완료를 같은 트랜잭션에서 확정한다.

    Args:
        repository: PostgreSQL 인증 저장소.
        job: 실행권을 가져온 작업의 ID, 계정과 실행권 번호.

    Returns:
        None: 새 작업자가 실행권을 얻었으면 해당 작업자의 처리를 기다린다.
    """
    with repository.connection() as db:
        finish = (
            update(DeletionJob)
            .where(
                DeletionJob.id == job["id"],
                DeletionJob.status == "running",
                DeletionJob.attempt_count == job["attempt_count"],
            )
            .values(status="completed", completed_at=func.clock_timestamp())
            .returning(DeletionJob.user_id)
        )
        account_id = db.scalar(finish)
        if account_id is None:
            return
        sessions = select(LoginSession.id).where(LoginSession.user_id == account_id)
        db.execute(delete(RefreshToken).where(RefreshToken.session_id.in_(sessions)))
        db.execute(delete(LoginSession).where(LoginSession.user_id == account_id))
        db.execute(
            delete(User).where(User.id == account_id, User.status == "deletion_pending")
        )


def process_one(repository, delete_owned):
    """실행 가능한 탈퇴 작업 하나의 MongoDB와 PostgreSQL 데이터를 순서대로 정리한다.

    Args:
        repository: 인증 PostgreSQL 저장소.
        delete_owned: 계정 UUID 문자열로 소유 수사를 멱등하게 정리하는 호출 함수.

    Returns:
        bool: 실행할 작업이 있었으면 참, 실행 가능한 작업이 없으면 거짓.

    Raises:
        Exception: 정리 실패 시 작업을 다음 시도 대상으로 남기고 예외를 다시 전파한다.
    """
    job = claim_job(repository)
    if job is None:
        return False
    try:
        delete_owned(str(job["user_id"]))
        complete_job(repository, job)
    except Exception:
        postpone_job(repository, job)
        raise
    return True
