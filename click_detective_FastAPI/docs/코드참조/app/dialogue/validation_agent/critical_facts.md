# `app/dialogue/validation_agent_v1/critical_facts.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/validation_agent_v1/critical_facts.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 207줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

명시적 수량·시각 귀속·일부 목적 표현의 규칙 검사. 일반 의미 이해를 대신하지 않는다.

정규식으로 읽을 수 있는 범위만 다룬다. 생략·동의어가 애매하면 검증 불가로 거절할
수 있으므로 원래 승인 의미를 유지한 재서술을 회귀 평가로 함께 확인해야 한다.

## 함께 읽을 코드

- [app/dialogue/schemas.py](../schemas.md)
- [app/dialogue/validation_agent_v1/semantic_verification.py](semantic_verification.md)
- [app/dialogue/validation_agent_v1/verification_units.py](verification_units.md)

## `quantity_anchors`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/critical_facts.py#L31)

```python
def quantity_anchors(text: str) -> set[tuple[int, str]]:
    ...
```

두 알과 2알 등을 같은 값으로 읽는다. 모든 한국어 수사를 해석하지는 않는다.

**파라미터**

- text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

**반환값**

set[tuple[int, str]]: 수량과 단위를 정규화한 집합.

## `time_anchors`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/critical_facts.py#L49)

```python
def time_anchors(text: str) -> set[tuple[int, int]]:
    ...
```

11시 2분·23:02의 시계상 위치를 비교한다. 오전/오후 추론은 모델에 남긴다.

**파라미터**

- text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

**반환값**

set[tuple[int, int]]: 비교할 시각의 시·분 집합.

## `time_actions`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/critical_facts.py#L64)

```python
def time_actions(text: str) -> set[tuple[tuple[int, int], str]]:
    ...
```

같은 문장에 명시된 숨기기·방문 행동과 시각을 연결한다. 문장 밖 추론은 하지 않는다.

**파라미터**

- text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

**반환값**

set[tuple[tuple[int, int], str]]: 같은 문장에 명시된 숨기기·방문 행동과 시각을 연결한다. 문장 밖 추론은 하지 않는다.

## `postponement_target`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/critical_facts.py#L88)

```python
def postponement_target(text: str) -> str | None:
    ...
```

발표·공개·일정·회의를 미루려는 명시적 목적 표현만 읽는다.

**파라미터**

- text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

**반환값**

str | None: 미루려는 대상으로 명시된 단어. 없으면 None.

## `critical_claim_error`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/critical_facts.py#L103)

```python
def critical_claim_error(request: CharacterReplyRequest, reply: str) -> str | None:
    ...
```

원문에 없는 명시적 수량·시각·행동 귀속과 읽을 수 있는 필수 목적 누락을 거절한다.

새 사건 사실의 근거는 allowed_facts뿐이다. 질문·인물 프로필·제시 자료·이력에서
숫자나 행동을 가져왔다고 승인하지 않는다. 오류에는 원문을 넣지 않는다.

**파라미터**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- reply (str): 의미를 검사하거나 문장으로 나눌 후보 대사.

**반환값**

str | None: 의미 변형 오류 코드. 규칙상 오류가 없으면 None.

## `critical_evidence_error`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/critical_facts.py#L147)

```python
def critical_evidence_error(unit_text: str, evidence_text: str) -> str | None:
    ...
```

모델이 true라고 해도 선택한 실제 근거에서 명시적 수량·시각이 빠지면 거절한다.

**파라미터**

- unit_text (str): 비교 기준인 승인 사실의 한 문장.
- evidence_text (str): 검증 보고서가 근거로 선택한 실제 후보 문장.

**반환값**

str | None: 실제 근거에 빠진 중요 의미의 오류 코드. 없으면 None.

## `predicate_anchors`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/critical_facts.py#L174)

```python
def predicate_anchors(text: str) -> set[str]:
    ...
```

방문·회수 의도·관찰 한계·흔들기·무반응·맥 확인 한계·질문의 명시적 표현을 읽는다.

알려진 누락 사례를 위한 제한된 표현 사전이며 한국어 전체의 논리 분석은 아니다.
같은 문장 안의 주체나 시제까지 완전하게 보장하지 않는다.

**파라미터**

- text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

**반환값**

set[str]: 문장에 명시된 행동과 관찰 한계 단서.
