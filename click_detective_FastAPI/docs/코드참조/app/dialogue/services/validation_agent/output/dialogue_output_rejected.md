# `app/dialogue/services/validation_agent/output/dialogue_output_rejected.py`

[코드 참조 목차](../../../../../README.md) · [도메인 목차](../../../README.md) · [실제 소스](../../../../../../../app/dialogue/services/validation_agent/output/dialogue_output_rejected.py)

대사 생성과 검증 과정의 안전한 실패 사유를 정의한다.

## `OutputRejected`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/output/dialogue_output_rejected.py#L4)

```python
class OutputRejected(ValueError):
    ...
```

고정 오류 코드와 안전한 하위 사유. 모델 원문·프롬프트는 담지 않는다.

**인자**

- code (str): 원문을 포함하지 않는 고정 오류 코드.
- detail (str): 오류를 구분하기 위한 추가 사유. 비밀값은 포함하지 않는다.

**반환값**

- OutputRejected: 위 역할을 수행하도록 생성된 객체.

## `OutputRejected.__init__`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/output/dialogue_output_rejected.py#L15)

```python
def __init__(self, code: str, detail: str='') -> None:
    ...
```

HTTP 코드는 유지하고 내부 형식 실패 원인을 별도로 추적한다.

**인자**

- code (str): 원문을 포함하지 않는 고정 오류 코드.
- detail (str): 오류를 구분하기 위한 추가 사유. 비밀값은 포함하지 않는다.

**반환값**

- None: 필요한 설정과 초기값을 저장한다.
