# `app/dialogue/services/validation_agent/evidence/dialogue_rules.py`

[코드 참조 목차](../../../../../README.md) · [도메인 목차](../../../README.md) · [실제 소스](../../../../../../../app/dialogue/services/validation_agent/evidence/dialogue_rules.py)

문장 코사인 유사도와 근거 검사 규칙.

## `normalize`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/evidence/dialogue_rules.py#L43)

```python
def normalize(text: str) -> str:
    ...
```

공백과 문장 끝 마침표를 정리한다.

**인자**

- text: 비교할 대사나 승인 사실.

**반환값**

- str: 비교용 문자열.

## `SentenceTransformerSimilarity`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/evidence/dialogue_rules.py#L55)

```python
class SentenceTransformerSimilarity:
    ...
```

요청에 포함된 문장들을 한 배치로 임베딩한다.

**인자**

- model_name: 로컬 모델 경로 또는 캐시에 준비된 모델 ID.
- device: 임베딩 실행 장치.

**반환값**

- SentenceTransformerSimilarity: 서버 프로세스에서 공유할 유사도 계산기.

## `SentenceTransformerSimilarity.__init__`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/evidence/dialogue_rules.py#L66)

```python
def __init__(self, model_name: str, device: str):
    ...
```

로컬 모델과 추론 잠금을 준비한다.

**인자**

- model_name: 모델 ID 또는 프로젝트 기준 상대 경로.
- device: 임베딩 실행 장치.

**반환값**

- None: 모델을 한 번 로드한다.

## `SentenceTransformerSimilarity.scores`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/evidence/dialogue_rules.py#L98)

```python
def scores(self, candidates: list[str], approved: list[str]):
    ...
```

정규화한 문장 벡터의 내적으로 코사인 유사도 행렬을 계산한다.

**인자**

- candidates: 생성된 후보 문장 목록.
- approved: 승인 사실의 검증 단위 목록.

**반환값**

- ndarray: 후보 문장 행과 승인 단위 열로 구성한 유사도 행렬.

## `preserves_anchors`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/evidence/dialogue_rules.py#L119)

```python
def preserves_anchors(source: str, candidate: str) -> bool:
    ...
```

코드가 인식할 수 있는 중요 사실의 누락·변경을 거절한다.

**인자**

- source: 근거가 되는 승인 사실 또는 공개 진술.
- candidate: 검증할 생성 문장.

**반환값**

- bool: 양방향 중요 사실 검사와 주체·양태 검사를 통과하면 True.

## `rule_match`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/evidence/dialogue_rules.py#L145)

```python
def rule_match(source: str, candidate: str) -> bool:
    ...
```

연결 어미 뒤 쉼표와 제한된 한국어 종결어미 차이를 허용한다.

**인자**

- source: 승인 원문 또는 공개 진술.
- candidate: 비교할 후보 문장.

**반환값**

- bool: 정규화한 문장이 같거나 허용된 어미 변화만 있으면 True.

## `public_sources`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/evidence/dialogue_rules.py#L173)

```python
def public_sources(request, history_limit: int) -> list[str]:
    ...
```

같은 인물에게 공개된 프로필과 이전 답변을 읽는다.

**인자**

- request: 현재 질문과 공개 프로필, 대화 이력.
- history_limit: 참조 가능한 최근 이력 수.

**반환값**

- list[str]: 질문자의 추측을 제외한 공개 답변 근거.
