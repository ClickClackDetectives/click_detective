# `tests/conftest.py`

[코드 참조 목차](../README.md) · [테스트 목차](README.md) · [실제 소스](../../../tests/conftest.py)

모든 테스트는 새 프로젝트 내부 데이터·임시 DB를 사용하고 HTTP 입력·출력을 기록한다.

## `redact`

[소스 선언](../../../tests/conftest.py#L17)

```python
def redact(value):
    ...
```

인증·게임 토큰은 JSON 보고서에서 숨긴다. 실제 질문·응답은 보존한다.

**인자**

- value: 검사·변환하거나 비밀값을 가릴 입력 값.

**반환값**

- 입력과 같은 구조의 값: 인증 정보와 알려진 비밀값을 가린 결과.

## `pytest_runtest_makereport`

[소스 선언](../../../tests/conftest.py#L49)

```python
def pytest_runtest_makereport(item, call):
    ...
```

검사 결과를 테스트 종료 후 보고서에서 읽을 수 있게 보관한다.

**인자**

- item: pytest 검사 항목 또는 처리할 데이터 항목.
- call: pytest가 제공하는 현재 실행 단계의 결과 정보.

**반환값**

- Iterator: with 또는 pytest 실행 동안 필요한 자원을 제공하는 반복자. 종료 시 정리 작업을 수행한다.

## `results`

[소스 선언](../../../tests/conftest.py#L64)

```python
def results():
    ...
```

모든 검사 결과와 HTTP 왕복을 하나의 JSON에 저장한다.

**인자**

- 없음.

**반환값**

- Iterator: with 또는 pytest 실행 동안 필요한 자원을 제공하는 반복자. 종료 시 정리 작업을 수행한다.

## `record`

[소스 선언](../../../tests/conftest.py#L92)

```python
def record(request, results):
    ...
```

HTTP가 없는 규칙 테스트도 보고서에서 빠뜨리지 않는다.

**인자**

- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.
- results: pytest 결과와 HTTP 기록을 모을 목록.

**반환값**

- Iterator: with 또는 pytest 실행 동안 필요한 자원을 제공하는 반복자. 종료 시 정리 작업을 수행한다.

## `service_key`

[소스 선언](../../../tests/conftest.py#L117)

```python
def service_key():
    ...
```

검사 서버와 HTTP 호출에 같은 서비스 키를 제공한다.

**인자**

- 없음.

**반환값**

- str: 테스트용 키.

## `client`

[소스 선언](../../../tests/conftest.py#L130)

```python
def client(fixture_settings):
    ...
```

HTTP 테스트용 FastAPI 클라이언트를 실행한다.

**인자**

- fixture_settings: GPU 없이 실행할 FastAPI 설정.

**반환값**

- Iterator: 실행 중인 HTTP 테스트 클라이언트.

## `api`

[소스 선언](../../../tests/conftest.py#L144)

```python
def api(client, request):
    ...
```

실제 응답을 assertion 이전에 기록하는 호출 함수를 제공한다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.
- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

**반환값**

- 실제 응답을 assertion 이전에 기록하는 호출 함수를 제공한다.

## `game`

[소스 선언](../../../tests/conftest.py#L198)

```python
def game(api):
    ...
```

현재 실제 사건 버전으로 독립 수사를 만든다.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.

**반환값**

- dict: 접근 토큰과 사건 버전을 확인한 내부 수사 상태.

## `play`

[소스 선언](../../../tests/conftest.py#L222)

```python
def play(api, game):
    ...
```

상태 변경의 새 revision을 보관하는 실제 게임 API 실행 도우미.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

**반환값**

- 상태 변경의 새 revision을 보관하는 실제 게임 API 실행 도우미.
