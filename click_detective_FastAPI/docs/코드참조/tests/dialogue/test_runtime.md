# `tests/dialogue/test_runtime.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/dialogue/test_runtime.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 181줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

dialogue/test_runtime.py의 회귀 동작을 확인한다.

## 함께 읽을 코드

- [app/dialogue/interrogation_graph.py](../../app/dialogue/interrogation_graph.md)
- [app/dialogue/schemas.py](../../app/dialogue/schemas.md)
- [app/schemas.py](../../app/investigation/api/schemas.md)
- [tests/dialogue/models.py](models.md)

## `test_three_agents_execute_with_backend_approval`

[소스 선언 위치](../../../../tests/dialogue/test_runtime.py#L16)

```python
async def test_three_agents_execute_with_backend_approval(client, game):
    ...
```

전처리·생성·검증 노드와 내부 승인 DTO가 실제로 연결되는지 검사한다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_generation_failure_does_not_consume_state`

[소스 선언 위치](../../../../tests/dialogue/test_runtime.py#L48)

```python
def test_generation_failure_does_not_consume_state(api, client, game, monkeypatch):
    ...
```

모델 실패가 질문·진술·revision을 변경하지 않으며 같은 요청을 재시도할 수 있다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- client: HTTP 요청을 실행하는 클라이언트.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_generation_failure_does_not_consume_state.FailingGraph`

[소스 선언 위치](../../../../tests/dialogue/test_runtime.py#L61)

```python
class FailingGraph:
    ...
```

검증 또는 추론 실패를 HTTP 오류로 재현한다.

**파라미터**

- 없음.

**반환값**

FailingGraph: 위 역할을 수행하도록 생성된 객체.

## `test_generation_failure_does_not_consume_state.FailingGraph.generate`

[소스 선언 위치](../../../../tests/dialogue/test_runtime.py#L71)

```python
async def generate(self, request):
    ...
```

실제 GPU를 사용하지 않는다.

**파라미터**

- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

**반환값**

str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `test_state_change_during_generation_rejects_stale_reply`

[소스 선언 위치](../../../../tests/dialogue/test_runtime.py#L103)

```python
async def test_state_change_during_generation_rejects_stale_reply(
    client, game, monkeypatch
):
    ...
```

생성 중 다른 행동이 확정되면 오래된 대사를 저장하지 않는다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_state_change_during_generation_rejects_stale_reply.WaitingGraph`

[소스 선언 위치](../../../../tests/dialogue/test_runtime.py#L118)

```python
class WaitingGraph:
    ...
```

모델 대기 동안 다른 API의 상태 변경이 가능한 상황을 재현한다.

**파라미터**

- 없음.

**반환값**

WaitingGraph: 위 역할을 수행하도록 생성된 객체.

## `test_state_change_during_generation_rejects_stale_reply.WaitingGraph.generate`

[소스 선언 위치](../../../../tests/dialogue/test_runtime.py#L128)

```python
async def generate(self, request):
    ...
```

승인 원문을 응답하더라도 revision이 달라지면 저장 단계에서 거절돼야 한다.

**파라미터**

- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

**반환값**

str: 호출 목적에 맞게 생성한 모델 출력 원문.
