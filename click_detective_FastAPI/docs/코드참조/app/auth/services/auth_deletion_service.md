# `app/auth/services/auth_deletion_service.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/services/auth_deletion_service.py)

계정 탈퇴 작업의 수사와 계정 데이터 정리를 조정한다.

## `process_one`

[소스 선언](../../../../../app/auth/services/auth_deletion_service.py#L10)

```python
def process_one(repository, delete_owned):
    ...
```

실행 가능한 탈퇴 작업 하나의 MongoDB와 PostgreSQL 데이터를 순서대로 정리한다.

**인자**

- repository: 인증 PostgreSQL 저장소.
- delete_owned: 계정 UUID 문자열로 소유 수사를 멱등하게 정리하는 호출 함수.

**반환값**

- bool: 실행할 작업이 있었으면 참, 실행 가능한 작업이 없으면 거짓.

**예외**

- Exception: 정리 실패 시 작업을 다음 시도 대상으로 남기고 예외를 다시 전파한다.
