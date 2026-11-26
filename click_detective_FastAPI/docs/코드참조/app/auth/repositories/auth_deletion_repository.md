# `app/auth/repositories/auth_deletion_repository.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/repositories/auth_deletion_repository.py)

계정 탈퇴 요청과 저장소 정리 작업을 관리한다.

## `verify_deletion`

[소스 선언](../../../../../app/auth/repositories/auth_deletion_repository.py#L19)

```python
def verify_deletion(repository, passwords, user_id, password):
    ...
```

현재 비밀번호를 확인하고 탈퇴 작업을 멱등하게 등록한다.

**인자**

- repository: PostgreSQL 인증 저장소.
- passwords: 비밀번호 해시 검증기.
- user_id: 접근 JWT로 확인한 계정 UUID.
- password: 탈퇴를 확인하는 현재 비밀번호 원문.

**반환값**

- None: 탈퇴 작업 등록과 활성 세션 폐기가 확정된다.

## `claim_job`

[소스 선언](../../../../../app/auth/repositories/auth_deletion_repository.py#L74)

```python
def claim_job(repository):
    ...
```

대기 작업이나 임대 만료 작업 하나의 실행권을 가져온다.

**인자**

- repository: PostgreSQL 인증 저장소.

**반환값**

- dict | None: 작업 ID와 계정 UUID 및 실행권 번호, 또는 실행 가능한 작업 없음.

## `postpone_job`

[소스 선언](../../../../../app/auth/repositories/auth_deletion_repository.py#L108)

```python
def postpone_job(repository, job):
    ...
```

아직 자신이 보유한 작업만 다음 실행을 위해 대기 상태로 돌린다.

**인자**

- repository: PostgreSQL 인증 저장소.
- job: 실행권을 가져온 작업의 ID, 계정과 실행권 번호.

**반환값**

- None: 현재 실행권에 해당하는 작업의 다음 시도 시각을 저장한다.

## `complete_job`

[소스 선언](../../../../../app/auth/repositories/auth_deletion_repository.py#L135)

```python
def complete_job(repository, job):
    ...
```

현재 실행권을 확인하고 인증 데이터 및 작업 완료를 같은 트랜잭션에서 확정한다.

**인자**

- repository: PostgreSQL 인증 저장소.
- job: 실행권을 가져온 작업의 ID, 계정과 실행권 번호.

**반환값**

- None: 새 작업자가 실행권을 얻었으면 해당 작업자의 처리를 기다린다.
