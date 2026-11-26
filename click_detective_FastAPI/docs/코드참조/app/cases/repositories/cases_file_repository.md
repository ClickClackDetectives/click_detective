# `app/cases/repositories/cases_file_repository.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/cases/repositories/cases_file_repository.py)

복사된 데이터의 무결성을 확인하고 정적 사건·비공개 규칙을 서버에서만 읽는다.

## `Catalog`

[소스 선언](../../../../../app/cases/repositories/cases_file_repository.py#L10)

```python
class Catalog:
    ...
```

런타임은 Next.js나 TypeScript를 실행하지 않는다. 모든 데이터는 자체 data에서 읽는다.

**인자**

- root (Path): 정적 사건 데이터가 있는 최상위 디렉터리.

**반환값**

- Catalog: 위 역할을 수행하도록 생성된 객체.

## `Catalog.__init__`

[소스 선언](../../../../../app/cases/repositories/cases_file_repository.py#L20)

```python
def __init__(self, root: Path):
    ...
```

시작 시 파일 해시를 확인한다. 원본 프로젝트나 개인 플레이 기록은 읽지 않는다.

**인자**

- root (Path): 정적 사건 데이터가 있는 최상위 디렉터리.

**반환값**

- None: 필요한 설정과 초기값을 저장한다.

## `Catalog.read`

[소스 선언](../../../../../app/cases/repositories/cases_file_repository.py#L61)

```python
def read(self, name: str):
    ...
```

서버 코드가 지정한 정적 파일만 읽는다. 클라이언트 경로를 전달하지 않는다.

**인자**

- name (str): 읽을 파일 또는 실행할 사례의 이름.

**반환값**

- dict: 지정한 사건 JSON 파일에서 읽은 데이터.

## `Catalog.require_case`

[소스 선언](../../../../../app/cases/repositories/cases_file_repository.py#L72)

```python
def require_case(self, case_id):
    ...
```

실제 실행 가능한 사건을 검사한다. 예정 사건을 수사로 시작하지 않는다.

**인자**

- case_id: 조회하거나 생성할 사건의 식별자.

**반환값**

- None: 반환값 없음.

## `Catalog.public_asset`

[소스 선언](../../../../../app/cases/repositories/cases_file_repository.py#L84)

```python
def public_asset(self, path: str):
    ...
```

증거·비공개 JSON은 공개 정적 자산 경로로 제공하지 않는다.

**인자**

- path (str): 저장 파일 경로나 HTTP 요청 경로.

**반환값**

- Path: 공개 자산의 검증된 실제 파일 경로.
