# `app/dialogue/validation_agent_v1/output.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/validation_agent_v1/output.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 122줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

대사 출력 형식 검사와 승인 원문 복구를 담당한다.

## 함께 읽을 코드

- [app/dialogue/diagnostics.py](../diagnostics.md)
- [app/dialogue/reply_validation.py](../reply_validation.md)
- [app/dialogue/schemas.py](../schemas.md)
- [app/dialogue/state.py](../state.md)

## `ReplyOutput`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/output.py#L13)

```python
class ReplyOutput:
    ...
```

모델 출력의 형식 검사와 승인 원문 복구를 담당한다.

**파라미터**

- settings: 모델 실행과 검색에 사용할 설정.
- model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

**반환값**

ReplyOutput: 위 역할을 수행하도록 생성된 객체.

## `ReplyOutput.__init__`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/output.py#L24)

```python
def __init__(self, settings, model):
    ...
```

사용할 의존성과 초기 상태를 준비한다.

**파라미터**

- settings: 모델 실행과 검색에 사용할 설정.
- model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `ReplyOutput.parse`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/output.py#L37)

```python
def parse(self, request: CharacterReplyRequest, raw: str) -> CharacterReplyResponse:
    ...
```

JSON·길이·선택적 ID를 규칙으로 검사한다. 의미 검증은 별도 호출로 수행한다.

**파라미터**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- raw (str): 모델이 반환한 가공 전 출력 문자열.

**반환값**

CharacterReplyResponse: 출력 형식과 사실 ID를 검사한 후보 응답.

## `ReplyOutput.failure`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/output.py#L92)

```python
def failure(
    self, request: CharacterReplyRequest, status: int, code: str
) -> CharacterReplyResponse:
    ...
```

시도 상한 이후 고정 대체 응답이나 HTTP 오류로 처리한다.

**파라미터**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- status (int): 실패를 표현할 HTTP 상태 코드.
- code (str): 원문을 포함하지 않는 고정 오류 코드.

**반환값**

CharacterReplyResponse: 승인 원문으로 구성한 복구 응답. 복구 비허용 시 HTTPException을 발생시킨다.
