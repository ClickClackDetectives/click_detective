# `app/auth/repositories/auth_repository.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/repositories/auth_repository.py)

PostgreSQL 계정과 세션을 SQLAlchemy ORM으로 저장한다.

## `AuthRepository`

[소스 선언](../../../../../app/auth/repositories/auth_repository.py#L15)

```python
class AuthRepository:
    ...
```

계정과 세션의 연결 풀 및 짧은 ORM 트랜잭션을 관리한다.

**인자**

- dsn: PostgreSQL 연결 문자열.

**반환값**

- AuthRepository: 인증 계정 및 세션의 영속 저장소.

## `AuthRepository.__init__`

[소스 선언](../../../../../app/auth/repositories/auth_repository.py#L25)

```python
def __init__(self, dsn):
    ...
```

연결 풀을 열고 초기 스키마를 준비한다.

**인자**

- dsn: PostgreSQL 연결 문자열.

**반환값**

- None: 반환값 없음.

## `AuthRepository.close`

[소스 선언](../../../../../app/auth/repositories/auth_repository.py#L64)

```python
def close(self):
    ...
```

사용 중인 PostgreSQL 연결 풀을 닫는다.

**인자**

- 없음.

**반환값**

- None: 반환값 없음.

## `AuthRepository.connection`

[소스 선언](../../../../../app/auth/repositories/auth_repository.py#L76)

```python
def connection(self):
    ...
```

ORM 세션과 트랜잭션을 제공하고 연결 장애를 API 오류로 바꾼다.

**인자**

- 없음.

**반환값**

- ContextManager: 성공 시 확정하고 예외 시 롤백하는 ORM 세션.

## `AuthRepository.insert_user`

[소스 선언](../../../../../app/auth/repositories/auth_repository.py#L93)

```python
def insert_user(self, user):
    ...
```

고유 이메일을 기준으로 신규 계정을 등록한다.

**인자**

- user: 허용된 계정 등록 필드.

**반환값**

- bool: 계정을 삽입했으면 참, 기존 이메일이면 거짓.

## `AuthRepository.lookup`

[소스 선언](../../../../../app/auth/repositories/auth_repository.py#L109)

```python
def lookup(self, query):
    ...
```

활성 계정의 비밀번호 검증 정보를 조회한다.

**인자**

- query: 정규화한 이메일 키 입력.

**반환값**

- Mapping | None: 계정의 내부 등록 정보 또는 활성 계정 없음.

## `AuthRepository.insert_session`

[소스 선언](../../../../../app/auth/repositories/auth_repository.py#L124)

```python
def insert_session(self, session, password_hash, upgraded_hash):
    ...
```

검증한 계정의 세션과 최초 갱신 토큰을 함께 저장한다.

**인자**

- session: 세션과 첫 갱신 토큰의 저장 입력.
- password_hash: 로그인에서 검증한 비밀번호 해시.
- upgraded_hash: 현재 정책으로 갱신할 해시 또는 None.

**반환값**

- bool: 활성 계정의 검증한 자격 증명이 유효해서 저장했으면 참.

## `AuthRepository.active_user`

[소스 선언](../../../../../app/auth/repositories/auth_repository.py#L165)

```python
def active_user(self, user_id, session_id):
    ...
```

접근 JWT와 계정이 아직 유효한 세션에 속하는지 확인한다.

**인자**

- user_id: 검증한 JWT의 계정 UUID.
- session_id: 검증한 JWT의 세션 UUID.

**반환값**

- Mapping | None: 활성 계정 요약 또는 유효한 세션 없음.

## `AuthRepository.revoke`

[소스 선언](../../../../../app/auth/repositories/auth_repository.py#L189)

```python
def revoke(self, refresh_hash, identity, expected_user):
    ...
```

확인된 토큰이 가리키는 세션을 폐기한다.

**인자**

- refresh_hash: 갱신 토큰 해시 또는 None.
- identity: 갱신 토큰을 찾을 수 없을 때 사용할 계정 및 세션 UUID 쌍.
- expected_user: 로그아웃을 요청한 화면의 계정 ID 또는 None.

**반환값**

- None: 대상 세션이 없거나 이전에 폐기됐어도 성공한다.
