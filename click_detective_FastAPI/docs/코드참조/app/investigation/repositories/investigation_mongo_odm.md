# `app/investigation/repositories/investigation_mongo_odm.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/repositories/investigation_mongo_odm.py)

MongoEngine 쿼리를 기존 MongoDB 트랜잭션 세션에 연결한다.

## `SessionCollection`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_odm.py#L22)

```python
class SessionCollection:
    ...
```

MongoEngine 0.29 쿼리에 동일한 PyMongo 세션을 적용한다.

**인자**

- collection: ODM 모델의 기존 BSON 컬렉션.
- session: 한 트랜잭션에서 사용할 PyMongo 세션.

**반환값**

- SessionCollection: 트랜잭션 세션을 보유하는 컬렉션 어댑터.

## `SessionCollection.__init__`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_odm.py#L33)

```python
def __init__(self, collection, session):
    ...
```

컬렉션과 세션을 묶는다.

**인자**

- collection: PyMongo 컬렉션.
- session: 현재 트랜잭션 세션.

**반환값**

- None: 반환값 없음.

## `SessionCollection.with_options`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_odm.py#L46)

```python
def with_options(self, **options):
    ...
```

저장 옵션을 적용한 컬렉션에도 동일한 세션을 전달한다.

**인자**

- options: MongoEngine이 설정하는 읽기·쓰기 보장 옵션.

**반환값**

- SessionCollection: 갱신한 옵션과 기존 세션을 보관하는 어댑터.

## `SessionCollection.__getattr__`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_odm.py#L57)

```python
def __getattr__(self, name):
    ...
```

MongoEngine이 호출하는 컬렉션 기능에 세션을 전달한다.

**인자**

- name: ODM이 읽을 속성 또는 호출할 PyMongo 메서드 이름.

**반환값**

- object: 메타데이터 또는 트랜잭션 세션이 설정된 호출 함수.

## `preserve_driver_error`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_odm.py#L75)

```python
def preserve_driver_error():
    ...
```

ODM이 감싼 저장 오류를 기존 트랜잭션 재시도 계층에 전달한다.

**인자**

- 없음.

**반환값**

- ContextManager: MongoEngine 오류에서 드라이버 오류를 복구하는 문맥.

## `MappedCollection`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_odm.py#L93)

```python
class MappedCollection:
    ...
```

저장소마다 독립적인 컬렉션을 문서 모델에 연결한다.

**인자**

- model: MongoEngine 문서 모델.
- collection: 해당 저장소가 소유한 PyMongo 컬렉션.

**반환값**

- MappedCollection: 저장소 조회 및 이관에 사용할 문서 매핑.

## `MappedCollection.__init__`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_odm.py#L104)

```python
def __init__(self, model, collection):
    ...
```

문서 모델과 컬렉션의 연결을 설정한다.

**인자**

- model: MongoEngine 문서 모델.
- collection: 데이터베이스별 컬렉션.

**반환값**

- None: 반환값 없음.

## `MappedCollection.query`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_odm.py#L117)

```python
def query(self, session=None, **filters):
    ...
```

문서 필드 이름으로 MongoEngine 쿼리를 구성한다.

**인자**

- session: 조회 또는 변경이 포함될 트랜잭션. 일반 조회에서는 None.
- filters: ODM 문서 필드 기반의 조회 조건.

**반환값**

- QuerySet: 요청 단위로 생성한 MongoEngine 쿼리.

## `MappedCollection.insert`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_odm.py#L132)

```python
def insert(self, document, session):
    ...
```

검증한 ODM 문서를 현재 트랜잭션에 삽입한다.

**인자**

- document: 해당 컬렉션의 MongoEngine 문서.
- session: 수사와 요청 기록을 함께 확정할 트랜잭션 세션.

**반환값**

- None: 해당 문서의 삽입 작업을 완료한다.
