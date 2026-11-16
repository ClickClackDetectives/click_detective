# `app/investigation/storage.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/investigation/storage.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 67줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

수사 데이터베이스의 연결과 트랜잭션 수명을 관리한다.

## `InvestigationStorage`

[소스 선언 위치](../../../../app/investigation/storage.py#L10)

```python
class InvestigationStorage:
    ...
```

수사 데이터베이스의 연결을 제공한다.

**파라미터**

- path (Path): 저장 파일 경로나 HTTP 요청 경로.

**반환값**

InvestigationStorage: 위 역할을 수행하도록 생성된 객체.

## `InvestigationStorage.__init__`

[소스 선언 위치](../../../../app/investigation/storage.py#L20)

```python
def __init__(self, path: Path):
    ...
```

접근할 데이터베이스 경로를 보관한다.

**파라미터**

- path (Path): 저장 파일 경로나 HTTP 요청 경로.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `InvestigationStorage.transaction`

[소스 선언 위치](../../../../app/investigation/storage.py#L32)

```python
def transaction(self):
    ...
```

짧은 쓰기 트랜잭션을 제공한다. 실패 시 롤백하고 연결을 항상 닫는다.

**파라미터**

- 없음.

**반환값**

ContextManager: SQLite 연결을 제공하고 성공 시 commit, 실패 시 rollback하는 문맥 관리자.

## `digest`

[소스 선언 위치](../../../../app/investigation/storage.py#L54)

```python
def digest(value) -> str:
    ...
```

JSON 내용을 정규화해 같은 요청인지 비교한다. 값은 SQL에 바인딩한다.

**파라미터**

- value: 검사·변환하거나 비밀값을 가릴 입력 값.

**반환값**

str: 같은 JSON 입력을 비교할 SHA-256 해시.
