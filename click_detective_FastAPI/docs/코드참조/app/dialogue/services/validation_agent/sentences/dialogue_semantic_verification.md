# `app/dialogue/services/validation_agent/sentences/dialogue_semantic_verification.py`

[코드 참조 목차](../../../../../README.md) · [도메인 목차](../../../README.md) · [실제 소스](../../../../../../../app/dialogue/services/validation_agent/sentences/dialogue_semantic_verification.py)

모델이 인용문을 다시 쓰지 않고 후보 문장 번호를 선택하게 하는 의미 검증 계약.

## `CandidateSentence`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/sentences/dialogue_semantic_verification.py#L8)

```python
class CandidateSentence:
    ...
```

서버가 원본 대사에서 잘라낸 문장. 번호가 원문의 실제 구간에 연결된다.

**인자**

- id (int): 항목을 구분하는 식별자.
- start (int): 원문에서 문장이 시작하는 위치.
- end (int): 원문에서 문장이 끝나는 위치.
- text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

**반환값**

- CandidateSentence: 위 역할을 수행하도록 생성된 객체.

## `candidate_sentences`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/sentences/dialogue_semantic_verification.py#L27)

```python
def candidate_sentences(reply: str) -> list[CandidateSentence]:
    ...
```

문장 번호와 원문 위치를 만든다. 원문을 교정하거나 바꿔 인용을 맞추지 않는다.

**인자**

- reply (str): 의미를 검사하거나 문장으로 나눌 후보 대사.

**반환값**

- list[CandidateSentence]: 후보 문장의 번호, 원문 위치와 텍스트.
