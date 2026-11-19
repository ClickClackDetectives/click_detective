# `app/dialogue/validation_agent_v1/agent.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/validation_agent_v1/agent.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 128줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

후보 대사의 검증, 재생성 여부와 복구 응답을 결정한다.

## 함께 읽을 코드

- [app/dialogue/diagnostics.py](../diagnostics.md)
- [app/dialogue/local_model.py](../local_model.md)
- [app/dialogue/reply_validation.py](../reply_validation.md)
- [app/dialogue/state.py](../state.md)
- [app/dialogue/validation_agent_v1/meaning_guards.py](meaning_guards.md)
- [app/dialogue/validation_agent_v1/output.py](output.md)
- [app/dialogue/validation_agent_v1/report_policy.py](report_policy.md)
- [app/dialogue/validation_agent_v1/verification.py](verification.md)

## `ValidationAgent`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/agent.py#L17)

```python
class ValidationAgent:
    ...
```

후보 대사의 검사와 재생성·실패 처리를 조정한다.

**파라미터**

- settings: 모델 실행과 검색에 사용할 설정.
- model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

**반환값**

ValidationAgent: 위 역할을 수행하도록 생성된 객체.

## `ValidationAgent.__init__`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/agent.py#L28)

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

## `ValidationAgent.validation_agent`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/agent.py#L43)

```python
async def validation_agent(self, state: InterrogationState) -> dict:
    ...
```

에이전트 3: 규칙 검사 후 의미 검증을 수행하고 재생성 또는 최종 처리를 결정한다.

**파라미터**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

**반환값**

dict: 최종 응답 또는 재생성 여부와 거절 코드.
