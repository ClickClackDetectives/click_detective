# `app/dialogue/services/validation_agent/policy/dialogue_validation_policy.py`

[코드 참조 목차](../../../../../README.md) · [도메인 목차](../../../README.md) · [실제 소스](../../../../../../../app/dialogue/services/validation_agent/policy/dialogue_validation_policy.py)

규칙만으로 확정하기 어려운 판정을 로컬 오픈 LLM에 위임한다.

## `SentenceEvidence`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/policy/dialogue_validation_policy.py#L24)

```python
class SentenceEvidence(DTO):
    ...
```

후보 문장을 원본 승인 단위에 연결하는 검증 판정.

**인자**

- matches: 후보 문장 번호와 문장 전체를 뒷받침하는 승인 단위 번호 목록.

**반환값**

- SentenceEvidence: 정수 식별자만 담는 판정.

## `PublicDecision`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/policy/dialogue_validation_policy.py#L37)

```python
class PublicDecision(DTO):
    ...
```

후보 대사의 공개 범위 준수 여부.

**인자**

- allowed: 전체 대사가 공개 범위 안에 있는지 여부.

**반환값**

- PublicDecision: 공개 범위에 대한 판정.

## `HybridPolicy`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/policy/dialogue_validation_policy.py#L50)

```python
class HybridPolicy(RulePolicy):
    ...
```

규칙을 보완하는 로컬 오픈 LLM 정책.

**인자**

- settings: 검증 호출 제한을 담은 설정.
- model: verification 목적을 지원하는 로컬 모델.

**반환값**

- HybridPolicy: 불확실한 경우 모델 판정을 요청하는 정책.

## `HybridPolicy.__init__`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/policy/dialogue_validation_policy.py#L61)

```python
def __init__(self, settings, model):
    ...
```

동일 서버에 로드된 모델을 검증에 연결한다.

**인자**

- settings: 호출 시간과 배치 크기 설정.
- model: 모델 실행기.

**반환값**

- None: 모델과 설정을 보관한다.

## `HybridPolicy.judge`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/policy/dialogue_validation_policy.py#L74)

```python
async def judge(self, instruction, payload, schema):
    ...
```

검증을 한 번 호출하고 실패하면 확인 가능한 판정만 사용하도록 한다.

**인자**

- instruction: 모델의 판정 기준.
- payload: 승인 원문이나 공개 정보로 구성한 요청.
- schema: 모델의 구조화 출력 검증 형식.

**반환값**

- DTO | None: 확인된 판정 또는 호출·출력 오류.

## `HybridPolicy.public_allowed`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/policy/dialogue_validation_policy.py#L112)

```python
async def public_allowed(self, question, reply, sources):
    ...
```

공개 범위에 있는지 애매한 후보를 모델에 한 번 확인한다.

**인자**

- question: 질문자의 발화. 공개 사실의 근거가 아니다.
- reply: 검사할 대사.
- sources: 같은 인물의 공개 정보와 진술.

**반환값**

- bool: 공개 범위 준수가 확인되면 True.

## `HybridPolicy.supported_units`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/policy/dialogue_validation_policy.py#L141)

```python
async def supported_units(self, request, sentences, units, eligible):
    ...
```

규칙으로 확정하지 못한 문장만 모델로 재검증한다.

**인자**

- request: 현재 승인 범위와 질문을 담은 요청.
- sentences: 유사도 기준을 통과한 문장 목록.
- units: 승인 사실별 검증 단위.
- eligible: 각 후보 문장의 유사도 기준을 통과한 승인 단위 번호.

**반환값**

- dict: 배치 판정을 원래 후보 문장 번호로 변환한 결과와 확인된 승인 단위 번호.
