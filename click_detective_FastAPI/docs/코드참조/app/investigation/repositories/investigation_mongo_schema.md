# `app/investigation/repositories/investigation_mongo_schema.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/repositories/investigation_mongo_schema.py)

새 MongoDB 수사 컬렉션의 최소 BSON 계약을 정의한다.

## `ensure_collection`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_schema.py#L33)

```python
def ensure_collection(database, name, fields, conditions):
    ...
```

컬렉션이 처음 만들어질 때 문서 validator를 설정한다.

**인자**

- database: 해당 컬렉션을 저장할 MongoDB 데이터베이스.
- name: 컬렉션 이름.
- fields: 반드시 존재해야 하는 필드와 BSON 스키마.
- conditions: 필드 사이에 추가로 성립해야 하는 조회 조건.

**반환값**

- None: 신규 컬렉션을 만들거나 기존 컬렉션을 그대로 사용한다.

## `prepare_collections`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_schema.py#L57)

```python
def prepare_collections(database):
    ...
```

수사와 행동 요청 컬렉션을 준비한다.

**인자**

- database: 수사 저장에 사용할 MongoDB 데이터베이스.

**반환값**

- None: 두 컬렉션의 최초 생성 작업을 마친다.
