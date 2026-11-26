# `app/dialogue/services/inference_agent/dialogue_inference_agent.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/dialogue/services/inference_agent/dialogue_inference_agent.py)

InferenceAgent의 처리 순서를 담는다.

## `InferenceAgent`

[소스 선언](../../../../../../app/dialogue/services/inference_agent/dialogue_inference_agent.py#L15)

```python
class InferenceAgent:
    ...
```

모델에 후보 대사 생성을 요청한다.

**인자**

- settings: 검색과 생성 실행에 사용할 설정.
- model: 대사 생성에 사용할 공용 모델. 전처리에서는 직접 호출하지 않는다.

**반환값**

- InferenceAgent: 해당 단계의 작업을 수행하는 객체.

## `InferenceAgent.__init__`

[소스 선언](../../../../../../app/dialogue/services/inference_agent/dialogue_inference_agent.py#L26)

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

## `InferenceAgent.inference_agent`

[소스 선언](../../../../../../app/dialogue/services/inference_agent/dialogue_inference_agent.py#L39)

```python
async def inference_agent(self, state: InterrogationState) -> dict:
    ...
```

에이전트 2: 사실의 의미를 유지하며 표현을 샘플링한다. 원문 복사를 요구하지 않는다.

**인자**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

**반환값**

- dict: 후보 대사 또는 실행 오류 상태.
