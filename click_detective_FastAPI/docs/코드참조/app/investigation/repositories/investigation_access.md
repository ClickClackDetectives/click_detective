# `app/investigation/repositories/investigation_access.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/repositories/investigation_access.py)

수사 접근 방식을 표현하고 저장된 소유권을 확인한다.

## `AccountAccess`

[소스 선언](../../../../../app/investigation/repositories/investigation_access.py#L9)

```python
class AccountAccess:
    ...
```

인증 서비스에서 확인한 계정의 수사 접근 권한을 나타낸다.

**인자**

- user_id: 인증을 통과한 계정 UUID.

**반환값**

- AccountAccess: 저장소에 전달할 계정 접근 문맥.

## `token_hash`

[소스 선언](../../../../../app/investigation/repositories/investigation_access.py#L22)

```python
def token_hash(token: str) -> str:
    ...
```

익명 수사 토큰을 SHA-256 형식으로 변환한다.

**인자**

- token: 서버가 발급한 익명 수사 토큰.

**반환값**

- str: 토큰의 16진수 해시.

## `allows_access`

[소스 선언](../../../../../app/investigation/repositories/investigation_access.py#L34)

```python
def allows_access(owner: str | None, hashed: str | None, access: str | AccountAccess) -> bool:
    ...
```

저장한 수사의 접근 방식에 맞춰 소유권을 확인한다.

**인자**

- owner: 계정 소유자 또는 익명 수사의 None.
- hashed: 익명 토큰 해시 또는 계정 수사의 None.
- access: 익명 수사 토큰 또는 검증된 계정 문맥.

**반환값**

- bool: 주어진 접근 문맥으로 수사를 열 수 있는지 여부.
