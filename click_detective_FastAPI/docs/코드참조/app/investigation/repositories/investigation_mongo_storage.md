# `app/investigation/repositories/investigation_mongo_storage.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/repositories/investigation_mongo_storage.py)

MongoDB 수사 컬렉션, 인덱스와 트랜잭션을 관리한다.

## `MongoStorage`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_storage.py#L24)

```python
class MongoStorage:
    ...
```

수사 저장에 사용할 MongoDB 연결과 트랜잭션을 제공한다.

**인자**

- uri: replica set 또는 샤드 클러스터의 접속 문자열.
- database: 수사 컬렉션을 보관할 데이터베이스 이름.

**반환값**

- MongoStorage: 수사 저장소의 연결과 공통 읽기 경계.

## `MongoStorage.__init__`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_storage.py#L35)

```python
def __init__(self, uri, database):
    ...
```

MongoDB의 트랜잭션 지원을 확인하고 수사 인덱스를 준비한다.

**인자**

- uri: replica set 또는 샤드 클러스터의 접속 문자열.
- database: 수사 컬렉션을 보관할 데이터베이스 이름.

**반환값**

- None: 초기 연결 및 인덱스 준비를 끝낸다.

## `MongoStorage.close`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_storage.py#L75)

```python
def close(self):
    ...
```

MongoDB 클라이언트와 연결 풀을 닫는다.

**인자**

- 없음.

**반환값**

- None: 반환값 없음.

## `MongoStorage.transaction`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_storage.py#L86)

```python
def transaction(self, apply):
    ...
```

수사와 요청 문서의 변경을 하나의 트랜잭션에서 확정한다.

**인자**

- apply: 세션을 받아 DB 작업만 수행하는 재시도 가능한 콜백.

**반환값**

- object: 성공한 콜백의 반환값.

## `MongoStorage.authorized_game`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_storage.py#L123)

```python
def authorized_game(self, game_id, access, session=None):
    ...
```

요청 문맥으로 접근할 수 있는 수사 문서를 조회한다.

**인자**

- game_id: 조회할 수사의 문자열 UUID.
- access: 익명 수사 토큰 또는 검증한 계정 문맥.
- session: 조회를 포함하는 트랜잭션 세션. 일반 읽기는 None.

**반환값**

- InvestigationDocument: 접근 가능함을 확인한 수사 문서.

## `MongoStorage.guard_owner_write`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_storage.py#L141)

```python
def guard_owner_write(self, user_id, session):
    ...
```

수사 생성·연결 트랜잭션을 계정의 탈퇴 차단과 직렬화한다.

**인자**

- user_id: PostgreSQL 인증 계정의 UUID.
- session: 수사와 함께 확정할 MongoDB 트랜잭션 세션.

**반환값**

- None: 탈퇴로 영구 차단된 계정이면 세션 오류를 낸다.

## `MongoStorage.block_owner_writes`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_storage.py#L159)

```python
def block_owner_writes(self, user_id):
    ...
```

탈퇴를 시작하면서 이후의 수사 생성·연결을 차단한다.

**인자**

- user_id: 모든 세션이 폐기된 탈퇴 계정 UUID.

**반환값**

- None: 지연된 요청을 막을 차단 기록을 유지한다.
