# `app/dialogue/services/validation_agent/output/dialogue_output.py`

[코드 참조 목차](../../../../../README.md) · [도메인 목차](../../../README.md) · [실제 소스](../../../../../../../app/dialogue/services/validation_agent/output/dialogue_output.py)

모델 대사의 형식과 사실 식별자를 검사한다.

## `ReplyOutput`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/output/dialogue_output.py#L16)

```python
class ReplyOutput:
    ...
```

모델 출력의 형식과 승인 사실 ID를 검사한다.

**인자**

- settings: 모델 실행과 검색에 사용할 설정.
- model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

**반환값**

- ReplyOutput: 위 역할을 수행하도록 생성된 객체.

## `ReplyOutput.__init__`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/output/dialogue_output.py#L27)

```python
def __init__(self, settings, model):
    ...
```

사용할 의존성과 초기 상태를 준비한다.

**인자**

- settings: 모델 실행과 검색에 사용할 설정.
- model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

**반환값**

- None: 필요한 설정과 초기값을 저장한다.

## `ReplyOutput.parse`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/output/dialogue_output.py#L40)

```python
def parse(self, request: CharacterReplyRequest, raw: str) -> CharacterReplyResponse:
    ...
```

JSON·길이·선택적 ID를 규칙으로 검사한다. 의미 검증은 별도 호출로 수행한다.

**인자**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- raw (str): 모델이 반환한 가공 전 출력 문자열.

**반환값**

- CharacterReplyResponse: 출력 형식과 사실 ID를 검사한 후보 응답.
