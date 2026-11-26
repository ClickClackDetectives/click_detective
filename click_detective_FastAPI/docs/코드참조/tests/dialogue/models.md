# `tests/dialogue/models.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/dialogue/models.py)

LangGraph 생성·검증 호출을 재현하는 모의 모델이다.

## `ApprovedModel`

[소스 선언](../../../../tests/dialogue/models.py#L6)

```python
class ApprovedModel:
    ...
```

승인 원문을 사용해 LangGraph의 생성·검증 호출을 재현하는 모의 모델.

**인자**

- 없음.

**반환값**

- ApprovedModel: 위 역할을 수행하도록 생성된 객체.

## `ApprovedModel.__init__`

[소스 선언](../../../../tests/dialogue/models.py#L18)

```python
def __init__(self):
    ...
```

호출 횟수로 생성과 별도 검증이 실제 실행됐는지 확인한다.

**인자**

- 없음.

**반환값**

- None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.

## `ApprovedModel.generate`

[소스 선언](../../../../tests/dialogue/models.py#L29)

```python
async def generate(self, messages, *, purpose='dialogue'):
    ...
```

생성은 승인 원문을 연결하고 추가 모델 판정에서는 불확실한 문장을 보류한다.

**인자**

- messages: 모델에 전달할 역할별 프롬프트 목록.
- purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

**반환값**

- str: 호출 목적에 맞게 생성한 모델 출력 원문.
