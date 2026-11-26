# `tests/dialogue/test_runner.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/dialogue/test_runner.py)

live_dialogue/test_runner.py의 회귀 동작을 확인한다.

## `runner`

[소스 선언](../../../../tests/dialogue/test_runner.py#L18)

```python
def runner(client):
    ...
```

네트워크 대신 임시 FastAPI fixture로 요청을 전달한다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

- LiveLlmTester: 네트워크 대신 테스트 앱을 호출하는 실서버 검사기.

## `StubGraph`

[소스 선언](../../../../tests/dialogue/test_runner.py#L54)

```python
class StubGraph:
    ...
```

모델이 아닌 도구 검사용 stop 응답. 실제 GPU 실행 증거가 아니다.

**인자**

- 없음.

**반환값**

- StubGraph: 위 역할을 수행하도록 생성된 객체.

## `StubGraph.generate`

[소스 선언](../../../../tests/dialogue/test_runner.py#L64)

```python
async def generate(self, request):
    ...
```

승인 문장을 반환해 HTTP 저장·보고서 계약만 검사한다.

**인자**

- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

**반환값**

- str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `test_live_agents_only_calls_graph_without_game`

[소스 선언](../../../../tests/dialogue/test_runner.py#L84)

```python
def test_live_agents_only_calls_graph_without_game(client, monkeypatch, tmp_path):
    ...
```

인증과 활성화 조건을 확인하고 게임 없이 에이전트 결과를 보고한다.

**인자**

- client: 테스트 앱 HTTP 클라이언트.
- monkeypatch: 테스트 동안 서버 설정과 그래프를 교체하는 도구.
- tmp_path: 진단 JSONL을 저장할 임시 경로.

**반환값**

- None: 권한 검사와 입출력·시간 보고서를 검증한다.

## `test_live_runner_rejects_fixture_200`

[소스 선언](../../../../tests/dialogue/test_runner.py#L143)

```python
def test_live_runner_rejects_fixture_200(client):
    ...
```

200이어도 fixed 응답은 실제 LLM 성공으로 오인하지 않는다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_live_runner_selected_cases_and_commit_checks`

[소스 선언](../../../../tests/dialogue/test_runner.py#L163)

```python
def test_live_runner_selected_cases_and_commit_checks(client, monkeypatch):
    ...
```

선택한 심문만 실행하고 버전·대화·쟁점·복원까지 확인한다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_live_runner_generation_failure_keeps_error_and_input`

[소스 선언](../../../../tests/dialogue/test_runner.py#L193)

```python
def test_live_runner_generation_failure_keeps_error_and_input(client, monkeypatch):
    ...
```

검증 오류 코드·질문·UUID를 오류 후에도 보존한다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
