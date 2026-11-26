# `tests/dialogue/test_free_question_recovery.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/dialogue/test_free_question_recovery.py)

증거 없는 자유 질문과 생성 재시도 계약을 실제 사건 데이터·3노드 그래프로 회귀 검사한다.

## `RetryingModel`

[소스 선언](../../../../tests/dialogue/test_free_question_recovery.py#L9)

```python
class RetryingModel:
    ...
```

첫 생성은 필수 뒷문장을 누락하고 다음 생성은 모두 포함하는 모의 모델.

**인자**

- 없음.

**반환값**

- RetryingModel: 위 역할을 수행하도록 생성된 객체.

## `RetryingModel.__init__`

[소스 선언](../../../../tests/dialogue/test_free_question_recovery.py#L21)

```python
def __init__(self):
    ...
```

사용할 의존성과 초기 상태를 준비한다.

**인자**

- 없음.

**반환값**

- None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.

## `RetryingModel.generate`

[소스 선언](../../../../tests/dialogue/test_free_question_recovery.py#L32)

```python
async def generate(self, messages, *, purpose='dialogue'):
    ...
```

실제 GPU 없이 생성 누락→검증 거절→올바른 평문 재생성을 재현한다.

**인자**

- messages: 모델에 전달할 역할별 프롬프트 목록.
- purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

**반환값**

- str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `test_unknown_free_question_returns_neutral`

[소스 선언](../../../../tests/dialogue/test_free_question_recovery.py#L74)

```python
def test_unknown_free_question_returns_neutral(api, client, game, monkeypatch):
    ...
```

승인 정보가 없는 질문은 502·허구 생성 대신 기존 중립 정책으로 응답한다.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- client: HTTP 요청을 실행하는 클라이언트.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
