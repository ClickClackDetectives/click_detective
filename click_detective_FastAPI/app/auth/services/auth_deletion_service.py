"""계정 탈퇴 작업의 수사와 계정 데이터 정리를 조정한다."""

from app.auth.repositories.auth_deletion_repository import (
    claim_job,
    complete_job,
    postpone_job,
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
