# `app/dialogue/inference_agent/agent.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/inference_agent/agent.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 105줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

InferenceAgent의 처리 순서를 담는다.

## 함께 읽을 코드

- [app/dialogue/diagnostics.py](../diagnostics.md)
- [app/dialogue/local_model.py](../local_model.md)
- [app/dialogue/reply_validation.py](../reply_validation.md)
- [app/dialogue/state.py](../state.md)

## `InferenceAgent`

[소스 선언 위치](../../../../../app/dialogue/inference_agent/agent.py#L15)

```python
class InferenceAgent:
    ...
```

모델에 후보 대사 생성을 요청한다.

**파라미터**

- settings: 검색과 생성 실행에 사용할 설정.
- model: 대사 생성에 사용할 공용 모델. 전처리에서는 직접 호출하지 않는다.

**반환값**

InferenceAgent: 해당 단계의 작업을 수행하는 객체.

## `InferenceAgent.__init__`

[소스 선언 위치](../../../../../app/dialogue/inference_agent/agent.py#L26)

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

## `InferenceAgent.inference_agent`

[소스 선언 위치](../../../../../app/dialogue/inference_agent/agent.py#L39)

```python
async def inference_agent(self, state: InterrogationState) -> dict:
    ...
```

에이전트 2: 사실의 의미를 유지하며 표현을 샘플링한다. 원문 복사를 요구하지 않는다.

**파라미터**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

**반환값**

dict: 후보 대사와 시도 횟수 또는 실행 오류 상태.
