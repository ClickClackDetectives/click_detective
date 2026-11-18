# `tests/dialogue/test_free_question_recovery.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/dialogue/test_free_question_recovery.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 204줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

증거 없는 자유 질문과 생성 재시도 계약을 실제 사건 데이터·3노드 그래프로 회귀 검사한다.

## 함께 읽을 코드

- [app/dialogue/interrogation_graph.py](../../app/dialogue/interrogation_graph.md)
- [app/dialogue/semantic_verification.py](../../app/dialogue/validation_agent/semantic_verification.md)
- [app/dialogue/verification_units.py](../../app/dialogue/validation_agent/verification_units.md)
- [app/schemas.py](../../app/investigation/api/schemas.md)

## `RetryingModel`

[소스 선언 위치](../../../../tests/dialogue/test_free_question_recovery.py#L14)

```python
class RetryingModel:
    ...
```

첫 생성은 필수 뒷문장을 누락하고 다음 생성은 모두 포함하는 모의 모델.

**파라미터**

- 없음.

**반환값**

RetryingModel: 위 역할을 수행하도록 생성된 객체.

## `RetryingModel.__init__`

[소스 선언 위치](../../../../tests/dialogue/test_free_question_recovery.py#L26)

```python
def __init__(self):
    ...
```

사용할 의존성과 초기 상태를 준비한다.

**파라미터**

- 없음.

**반환값**

None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.

## `RetryingModel.generate`

[소스 선언 위치](../../../../tests/dialogue/test_free_question_recovery.py#L37)

```python
async def generate(self, messages, *, purpose="dialogue"):
    ...
```

실제 GPU 없이 생성 누락→검증 거절→올바른 평문 재생성을 재현한다.

**파라미터**

- messages: 모델에 전달할 역할별 프롬프트 목록.
- purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

**반환값**

str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `test_no_evidence_question_can_retry_as_plain_text`

[소스 선언 위치](../../../../tests/dialogue/test_free_question_recovery.py#L79)

```python
async def test_no_evidence_question_can_retry_as_plain_text(client):
    ...
```

강민호 면담 질문의 첫 필수 문장 누락을 평문 형식을 유지하며 복구한다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_unknown_free_question_returns_neutral_without_model`

[소스 선언 위치](../../../../tests/dialogue/test_free_question_recovery.py#L109)

```python
def test_unknown_free_question_returns_neutral_without_model(
    api, client, game, monkeypatch
):
    ...
```

승인 정보가 없는 질문은 502·허구 생성 대신 기존 중립 정책으로 응답한다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- client: HTTP 요청을 실행하는 클라이언트.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_unknown_free_question_returns_neutral_without_model.NeverModel`

[소스 선언 위치](../../../../tests/dialogue/test_free_question_recovery.py#L124)

```python
class NeverModel:
    ...
```

호출되면 실패하는 모델로 빈 승인 경로의 GPU 미호출을 확인한다.

**파라미터**

- 없음.

**반환값**

NeverModel: 위 역할을 수행하도록 생성된 객체.

## `test_unknown_free_question_returns_neutral_without_model.NeverModel.generate`

[소스 선언 위치](../../../../tests/dialogue/test_free_question_recovery.py#L136)

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

## `test_false_verification_with_evidence_still_rejected`

[소스 선언 위치](../../../../tests/dialogue/test_free_question_recovery.py#L170)

```python
def test_false_verification_with_evidence_still_rejected(client):
    ...
```

검증 형식 안정화 과정에서도 false+근거 번호를 성공으로 수선하지 않는다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
