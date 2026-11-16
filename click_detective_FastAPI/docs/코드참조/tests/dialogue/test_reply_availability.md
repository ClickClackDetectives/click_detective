# `tests/dialogue/test_reply_availability.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/dialogue/test_reply_availability.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 208줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

게임에서 전송한 유효 질문은 모델 실패·쟁점 여부와 무관하게 답변을 확정한다.

## 함께 읽을 코드

- [app/config.py](../../app/config.md)
- [app/dialogue/interrogation_graph.py](../../app/dialogue/interrogation_graph.md)

## `test_valid_question_always_gets_approved_reply`

[소스 선언 위치](../../../../tests/dialogue/test_reply_availability.py#L22)

```python
def test_valid_question_always_gets_approved_reply(
    api, client, game, monkeypatch, failure
):
    ...
```

모델 실패는 200 fallback으로 복구하며 같은 UUID를 중복 소비하지 않는다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- client: HTTP 요청을 실행하는 클라이언트.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.
- failure: 테스트에서 재현할 실패 종류.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_valid_question_always_gets_approved_reply.FailingGraph`

[소스 선언 위치](../../../../tests/dialogue/test_reply_availability.py#L38)

```python
class FailingGraph:
    ...
```

모델 경로의 실패만 주입하고 승인·저장 로직은 실제 코드를 사용한다.

**파라미터**

- 없음.

**반환값**

FailingGraph: 위 역할을 수행하도록 생성된 객체.

## `test_valid_question_always_gets_approved_reply.FailingGraph.generate`

[소스 선언 위치](../../../../tests/dialogue/test_reply_availability.py#L50)

```python
async def generate(self, request):
    ...
```

호출 목적에 맞는 모델 출력을 만들거나 검사용 실패를 발생시킨다.

**파라미터**

- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

**반환값**

str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `test_failed_generated_admission_still_commits_only_approved_finding`

[소스 선언 위치](../../../../tests/dialogue/test_reply_availability.py#L88)

```python
def test_failed_generated_admission_still_commits_only_approved_finding(
    api, client, play, monkeypatch
):
    ...
```

복구 대사는 실제 획득·제시 조건을 통과한 쟁점만 기록한다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- client: HTTP 요청을 실행하는 클라이언트.
- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_failed_generated_admission_still_commits_only_approved_finding.FailingGraph`

[소스 선언 위치](../../../../tests/dialogue/test_reply_availability.py#L103)

```python
class FailingGraph:
    ...
```

모델 실패를 재현하여 복구와 상태 보존을 검사하는 모의 그래프다.

**파라미터**

- 없음.

**반환값**

FailingGraph: 위 역할을 수행하도록 생성된 객체.

## `test_failed_generated_admission_still_commits_only_approved_finding.FailingGraph.generate`

[소스 선언 위치](../../../../tests/dialogue/test_reply_availability.py#L113)

```python
async def generate(self, request):
    ...
```

호출 목적에 맞는 모델 출력을 만들거나 검사용 실패를 발생시킨다.

**파라미터**

- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

**반환값**

str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `test_real_graph_rejection_recovers_approved_fact`

[소스 선언 위치](../../../../tests/dialogue/test_reply_availability.py#L142)

```python
async def test_real_graph_rejection_recovers_approved_fact(client, monkeypatch):
    ...
```

3노드 그래프가 출력 형식을 거절해도 원문 복구가 이루어진다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_real_graph_rejection_recovers_approved_fact.InvalidModel`

[소스 선언 위치](../../../../tests/dialogue/test_reply_availability.py#L153)

```python
class InvalidModel:
    ...
```

출력 오류를 재현하는 모의 모델이다.

**파라미터**

- 없음.

**반환값**

InvalidModel: 위 역할을 수행하도록 생성된 객체.

## `test_real_graph_rejection_recovers_approved_fact.InvalidModel.generate`

[소스 선언 위치](../../../../tests/dialogue/test_reply_availability.py#L165)

```python
async def generate(self, messages, *, purpose="dialogue"):
    ...
```

호출 목적에 맞는 모델 출력을 만들거나 검사용 실패를 발생시킨다.

**파라미터**

- messages: 모델에 전달할 역할별 프롬프트 목록.
- purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

**반환값**

str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `test_default_player_policy_enables_reply_recovery`

[소스 선언 위치](../../../../tests/dialogue/test_reply_availability.py#L198)

```python
def test_default_player_policy_enables_reply_recovery():
    ...
```

신규 실행도 기본적으로 생성 오류를 플레이어에게 502로 내보내지 않는다.

**파라미터**

- 없음.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
