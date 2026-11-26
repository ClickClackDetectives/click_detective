# `app/dialogue/services/text/dialogue_text_relevance.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/dialogue/services/text/dialogue_text_relevance.py)

검증과 검색 평가가 공통으로 사용하는 키워드 관련성 점수.

## `_terms`

[소스 선언](../../../../../../app/dialogue/services/text/dialogue_text_relevance.py#L7)

```python
def _terms(text: str) -> set[str]:
    ...
```

표기를 통일한 단어를 추출한다.

**인자**

- text: 검색할 문장의 원문.

**반환값**

- set[str]: 정규화한 검색 단어.

## `_bigrams`

[소스 선언](../../../../../../app/dialogue/services/text/dialogue_text_relevance.py#L20)

```python
def _bigrams(terms: set[str]) -> set[str]:
    ...
```

조사가 붙은 단어의 부분 일치에 사용할 두 글자 조각을 얻는다.

**인자**

- terms: 정규화한 단어 집합.

**반환값**

- set[str]: 각 단어 안의 두 글자 조각.

## `text_relevance`

[소스 선언](../../../../../../app/dialogue/services/text/dialogue_text_relevance.py#L36)

```python
def text_relevance(question: str, fact_id: str, text: str) -> float:
    ...
```

팀 원본과 같은 ID·단어·두 글자 중복 점수를 계산한다.

**인자**

- question: 플레이어가 입력한 질문 원문.
- fact_id: 사실 또는 진술의 식별자.
- text: 검색용 진술 텍스트.

**반환값**

- float: ID 일치, 단어 일치와 부분 일치의 합.
