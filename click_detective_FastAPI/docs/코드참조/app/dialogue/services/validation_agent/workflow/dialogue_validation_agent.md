# `app/dialogue/services/validation_agent/workflow/dialogue_validation_agent.py`

[코드 참조 목차](../../../../../README.md) · [도메인 목차](../../../README.md) · [실제 소스](../../../../../../../app/dialogue/services/validation_agent/workflow/dialogue_validation_agent.py)

승인 사실 검증의 문장 필터, 재검증과 부분 응답을 조정한다.

## `neutral_response`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/workflow/dialogue_validation_agent.py#L28)

```python
def neutral_response(request):
    ...
```

승인 사실의 유무에 맞는 고정 대사를 반환한다.

**인자**

- request: 승인 범위와 응답 식별 정보를 가진 요청.

**반환값**

- CharacterReplyResponse: 승인 사실 전달을 기록하지 않는 중립 응답.

## `ValidationAgent`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/workflow/dialogue_validation_agent.py#L58)

```python
class ValidationAgent:
    ...
```

유사도 검사와 규칙·모델 판정으로 승인된 문장을 고른다.

**인자**

- settings: 유사도와 검증 조건을 지정한 설정.
- model: 검증 호출을 지원하는 로컬 모델.

**반환값**

- ValidationAgent: 전부·일부·중립 응답을 결정하는 검증 에이전트.

## `ValidationAgent.__init__`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/workflow/dialogue_validation_agent.py#L69)

```python
def __init__(self, settings, model):
    ...
```

판정 정책과 출력 파서를 준비한다.

**인자**

- settings: 검증 에이전트 설정.
- model: 서버가 로드한 모델.

**반환값**

- None: 에이전트의 실행 의존성을 저장한다.

## `ValidationAgent.validation_agent`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/workflow/dialogue_validation_agent.py#L86)

```python
async def validation_agent(self, state):
    ...
```

후보 대사를 검사하고 전부·일부·중립 중 하나로 종료한다.

**인자**

- state: 요청, 전처리 검증 단위, 후보 원문과 모델 오류를 담은 그래프 상태.

**반환값**

- dict: 승인된 최종 응답.

## `ValidationAgent.verify`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/workflow/dialogue_validation_agent.py#L117)

```python
async def verify(self, request, candidate, units):
    ...
```

공개 범위 검사 또는 세 단계 문장 검증을 수행한다.

**인자**

- request: 승인 사실과 현재 공개 문맥.
- candidate: 생성 모델이 반환한 대사.
- units: 생성 프롬프트를 구성할 때 사용한 승인 문장 단위.

**반환값**

- CharacterReplyResponse: 이번 판정의 최종 응답.

## `ValidationAgent.check_similarity`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/workflow/dialogue_validation_agent.py#L216)

```python
async def check_similarity(self, sentences, units):
    ...
```

대사 문장별로 유사도 기준을 만족하는 승인 단위를 고른다.

**인자**

- sentences: 원래 대사에 있는 문장 목록.
- units: 승인 사실을 분리한 검증 단위.

**반환값**

- dict: 문장 번호별 유사도 후보 목록.
