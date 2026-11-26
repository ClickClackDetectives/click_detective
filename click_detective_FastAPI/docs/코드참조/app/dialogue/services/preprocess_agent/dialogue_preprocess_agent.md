# `app/dialogue/services/preprocess_agent/dialogue_preprocess_agent.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/dialogue/services/preprocess_agent/dialogue_preprocess_agent.py)

PreprocessAgent의 처리 순서를 담는다.

## `PreprocessAgent`

[소스 선언](../../../../../../app/dialogue/services/preprocess_agent/dialogue_preprocess_agent.py#L18)

```python
class PreprocessAgent:
    ...
```

질문과 승인 사실을 정리한다.

**인자**

- settings: 생성 프롬프트에 사용할 설정.
- question_search: 게임 심문의 승인 진술을 검색하는 객체 또는 None.

**반환값**

- PreprocessAgent: 해당 단계의 작업을 수행하는 객체.

## `PreprocessAgent.__init__`

[소스 선언](../../../../../../app/dialogue/services/preprocess_agent/dialogue_preprocess_agent.py#L29)

```python
def __init__(self, settings, question_search=None):
    ...
```

사용할 의존성과 초기 상태를 준비한다.

**인자**

- settings: 생성 프롬프트에 사용할 설정.
- question_search: 게임 심문에 사용할 진술 검색기 또는 None.

**반환값**

- None: 필요한 설정과 초기값을 저장한다.

## `PreprocessAgent.preprocess_agent`

[소스 선언](../../../../../../app/dialogue/services/preprocess_agent/dialogue_preprocess_agent.py#L42)

```python
async def preprocess_agent(self, state: InterrogationState) -> dict:
    ...
```

게임의 공개 범위에서 진술을 검색하고 생성 문맥을 만든다.

**인자**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

**반환값**

- dict: 최종 승인 요청, 프롬프트, 검증 문장 목록, 초기 생성 횟수와 검색 결과가 비었는지 여부.
