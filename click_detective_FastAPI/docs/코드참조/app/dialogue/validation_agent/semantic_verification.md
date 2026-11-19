# `app/dialogue/validation_agent_v1/semantic_verification.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/validation_agent_v1/semantic_verification.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 80줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

모델이 인용문을 다시 쓰지 않고 후보 문장 번호를 선택하게 하는 의미 검증 계약.

## 함께 읽을 코드

- [app/dialogue/schemas.py](../schemas.md)

## `CandidateSentence`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/semantic_verification.py#L12)

```python
class CandidateSentence:
    ...
```

서버가 원본 대사에서 잘라낸 문장. 번호가 원문의 실제 구간에 연결된다.

**파라미터**

- id (int): 항목을 구분하는 식별자.
- start (int): 원문에서 문장이 시작하는 위치.
- end (int): 원문에서 문장이 끝나는 위치.
- text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

**반환값**

CandidateSentence: 위 역할을 수행하도록 생성된 객체.

## `candidate_sentences`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/semantic_verification.py#L31)

```python
def candidate_sentences(reply: str) -> list[CandidateSentence]:
    ...
```

문장 번호와 원문 위치를 만든다. 원문을 교정하거나 바꿔 인용을 맞추지 않는다.

**파라미터**

- reply (str): 의미를 검사하거나 문장으로 나눌 후보 대사.

**반환값**

list[CandidateSentence]: 후보 문장의 번호, 원문 위치와 텍스트.

## `SemanticReport`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/semantic_verification.py#L60)

```python
class SemanticReport(DTO):
    ...
```

짧은 검증 출력. 각 checks 항목은 [검증항목 번호, 포함 여부, 후보문장 번호 목록].

**파라미터**

- checks (list[tuple[StrictInt, StrictBool, list[StrictInt]]]): 승인 항목별 포함 여부와 근거 문장 번호 목록.
- has_contradiction (StrictBool): 승인 내용과 모순되는지 여부.
- has_unsupported_claims (StrictBool): 승인되지 않은 추가 주장이 있는지 여부.
- history_consistent (StrictBool): 이전 대화와 일관된지 여부.
- persona_consistent (StrictBool): 인물 설정과 일관된지 여부.
- uncertain (StrictBool): 의미 판정이 불확실한지 여부.

**반환값**

SemanticReport: 위 역할을 수행하도록 생성된 객체.
