# `app/dialogue/preprocess_agent/agent.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/preprocess_agent/agent.py)


## 파일의 역할

PreprocessAgent의 처리 순서를 담는다.

## 함께 읽을 코드

- [app/dialogue/diagnostics.py](../diagnostics.md)
- [app/dialogue/preprocess_agent/prompt.py](prompt.md)
- [app/dialogue/state.py](../state.md)
- [app/dialogue/validation_agent_v1/verification_units.py](../validation_agent/verification_units.md)

## `PreprocessAgent`

[소스 선언 위치](../../../../../app/dialogue/preprocess_agent/agent.py#L12)

```python
class PreprocessAgent:
    ...
```

질문과 승인 사실을 정리한다.

**파라미터**

- settings: 생성 프롬프트에 사용할 설정.

**반환값**

PreprocessAgent: 해당 단계의 작업을 수행하는 객체.

## `PreprocessAgent.__init__`

[소스 선언 위치](../../../../../app/dialogue/preprocess_agent/agent.py#L22)

```python
def __init__(self, settings):
    ...
```

사용할 의존성과 초기 상태를 준비한다.

**파라미터**

- settings: 생성 프롬프트에 사용할 설정.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `PreprocessAgent.preprocess_agent`

[소스 선언 위치](../../../../../app/dialogue/preprocess_agent/agent.py#L33)

```python
async def preprocess_agent(self, state: InterrogationState) -> dict:
    ...
```

승인된 사실과 검증 문장으로 생성 문맥을 만든다.

**파라미터**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

**반환값**

dict: 생성 프롬프트와 초기 생성 횟수.
