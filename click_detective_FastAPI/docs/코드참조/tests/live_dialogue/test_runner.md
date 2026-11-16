# `tests/live_dialogue/test_runner.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/live_dialogue/test_runner.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 175줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

live_dialogue/test_runner.py의 회귀 동작을 확인한다.

## 함께 읽을 코드

- [app/config.py](../../app/config.md)
- [app/dialogue/schemas.py](../../app/dialogue/schemas.md)
- [scripts/test_llm_api_live.py](../../scripts/test_llm_api_live.md)
- [tests/conftest.py](../conftest.md)

## `runner`

[소스 선언 위치](../../../../tests/live_dialogue/test_runner.py#L14)

```python
def runner(client):
    ...
```

네트워크 대신 임시 FastAPI fixture로 요청을 전달한다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

LiveLlmTester: 네트워크 대신 테스트 앱을 호출하는 실서버 검사기.

## `runner.send`

[소스 선언 위치](../../../../tests/live_dialogue/test_runner.py#L24)

```python
def send(request):
    ...
```

실서버 검사기의 요청을 테스트 클라이언트로 전달한다.

**파라미터**

- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

**반환값**

httpx.Response: 테스트 앱의 상태 코드·헤더·본문을 옮긴 HTTP 응답.

## `StubGraph`

[소스 선언 위치](../../../../tests/live_dialogue/test_runner.py#L50)

```python
class StubGraph:
    ...
```

모델이 아닌 도구 검사용 stop 응답. 실제 GPU 실행 증거가 아니다.

**파라미터**

- 없음.

**반환값**

StubGraph: 위 역할을 수행하도록 생성된 객체.

## `StubGraph.generate`

[소스 선언 위치](../../../../tests/live_dialogue/test_runner.py#L60)

```python
async def generate(self, request):
    ...
```

승인 문장을 반환해 HTTP 저장·보고서 계약만 검사한다.

**파라미터**

- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

**반환값**

str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `test_live_runner_rejects_fixture_200`

[소스 선언 위치](../../../../tests/live_dialogue/test_runner.py#L80)

```python
def test_live_runner_rejects_fixture_200(client):
    ...
```

200이어도 fixed 응답은 실제 LLM 성공으로 오인하지 않는다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_live_runner_selected_cases_and_commit_checks`

[소스 선언 위치](../../../../tests/live_dialogue/test_runner.py#L100)

```python
def test_live_runner_selected_cases_and_commit_checks(client, monkeypatch):
    ...
```

선택한 심문만 실행하고 버전·대화·쟁점·복원까지 확인한다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_live_runner_generation_failure_keeps_error_and_input`

[소스 선언 위치](../../../../tests/live_dialogue/test_runner.py#L130)

```python
def test_live_runner_generation_failure_keeps_error_and_input(client, monkeypatch):
    ...
```

검증 오류 코드·질문·UUID를 오류 후에도 보존한다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_live_runner_generation_failure_keeps_error_and_input.BrokenGraph`

[소스 선언 위치](../../../../tests/live_dialogue/test_runner.py#L141)

```python
class BrokenGraph:
    ...
```

모델 검증 실패 응답을 재현한다.

**파라미터**

- 없음.

**반환값**

BrokenGraph: 위 역할을 수행하도록 생성된 객체.

## `test_live_runner_generation_failure_keeps_error_and_input.BrokenGraph.generate`

[소스 선언 위치](../../../../tests/live_dialogue/test_runner.py#L151)

```python
async def generate(self, request):
    ...
```

호출 목적에 맞는 모델 출력을 만들거나 검사용 실패를 발생시킨다.

**파라미터**

- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

**반환값**

str: 호출 목적에 맞게 생성한 모델 출력 원문.
