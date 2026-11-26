# `tests/dialogue/test_runtime.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/dialogue/test_runtime.py)

dialogue/test_runtime.py의 회귀 동작을 확인한다.

## `test_three_agents_execute_with_backend_approval`

[소스 선언](../../../../tests/dialogue/test_runtime.py#L16)

```python
async def test_three_agents_execute_with_backend_approval(client, game, tmp_path):
    ...
```

전처리·생성·검증 노드와 내부 승인 DTO가 실제로 연결되는지 검사한다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
- tmp_path: 이 요청의 실행 진단을 저장할 임시 경로.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_generation_failure_charges_the_question_once`

[소스 선언](../../../../tests/dialogue/test_runtime.py#L57)

```python
def test_generation_failure_charges_the_question_once(api, client, game, monkeypatch):
    ...
```

받아들인 질문은 모델 실패 및 동일 요청 재전송에도 한 번만 차감한다.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- client: HTTP 요청을 실행하는 클라이언트.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_state_change_during_generation_rejects_stale_reply`

[소스 선언](../../../../tests/dialogue/test_runtime.py#L112)

```python
async def test_state_change_during_generation_rejects_stale_reply(client, game, monkeypatch):
    ...
```

생성 중 다른 행동이 확정되면 오래된 대사를 저장하지 않는다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_resubmitting_identical_question_as_new_action_charges_again`

[소스 선언](../../../../tests/dialogue/test_runtime.py#L194)

```python
def test_resubmitting_identical_question_as_new_action_charges_again(api, game):
    ...
```

같은 질문을 새로 제출하면 새 심문으로 차감하고 통신 재시도는 중복 차감하지 않는다.

**인자**

- api: 수사 API를 호출하는 테스트 도우미.
- game: 새 수사의 ID, 접근 토큰과 상태.

**반환값**

- None: 동일 질문을 두 번 제출한 뒤 저장된 심문 횟수를 검사한다.
