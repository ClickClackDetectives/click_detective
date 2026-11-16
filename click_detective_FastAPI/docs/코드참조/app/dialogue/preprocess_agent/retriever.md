# `app/dialogue/preprocess_agent/retriever.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/preprocess_agent/retriever.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 189줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

허용된 작은 사실 집합을 대상으로 하는 키워드 RAG.

첫 도입은 벡터 DB나 새 모델 없이 시작한다. 승인하지 않은 대본·정답·다른 수사의
기록은 검색하지 않는다. 검색 점수는 관련성 힌트이며 공개 권한·진실 판정이 아니다.

## 함께 읽을 코드

- [app/dialogue/schemas.py](../schemas.md)

## `RetrievedFact`

[소스 선언 위치](../../../../../app/dialogue/preprocess_agent/retriever.py#L15)

```python
class RetrievedFact:
    ...
```

선택 이유와 출처를 보관하는 서버 내부 검색 항목. 원본 파일 출처로 가장하지 않는다.

**파라미터**

- fact_id (str): 원래 승인 사실의 식별자.
- score (float): 질문과 사실의 관련성 점수.
- reason (str): 검색 결과가 선택된 이유.
- source_ref (str): 승인 사실 내 출처 참조.

**반환값**

RetrievedFact: 위 역할을 수행하도록 생성된 객체.

## `RetrievalContext`

[소스 선언 위치](../../../../../app/dialogue/preprocess_agent/retriever.py#L35)

```python
class RetrievalContext:
    ...
```

한 요청에서만 사용하는 검색 결과. 필수 사실은 top_k와 관계없이 보존한다.

**파라미터**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- case_id (str): 조회하거나 생성할 사건의 식별자.
- scenario_version (str): 현재 사건 데이터의 스냅샷 버전.
- suspect_id (str): 심문 대상 인물의 식별자.
- selected_facts (tuple[Fact, ...]): 검색으로 선택한 승인 사실 목록.
- hits (tuple[RetrievedFact, ...]): 사실별 검색 점수와 선택 이유.

**반환값**

RetrievalContext: 위 역할을 수행하도록 생성된 객체.

## `_terms`

[소스 선언 위치](../../../../../app/dialogue/preprocess_agent/retriever.py#L58)

```python
def _terms(text: str) -> set[str]:
    ...
```

표기를 통일한 단어를 얻는다. 한국어 형태소 분석이나 의미 추론은 수행하지 않는다.

**파라미터**

- text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

**반환값**

set[str]: 표기와 대소문자를 정규화한 검색 단어.

## `_bigrams`

[소스 선언 위치](../../../../../app/dialogue/preprocess_agent/retriever.py#L71)

```python
def _bigrams(terms: set[str]) -> set[str]:
    ...
```

조사가 붙은 한국어 단어의 부분 일치를 위해 두 글자 조각을 만든다.

**파라미터**

- terms (set[str]): 정규화한 검색 단어 집합.

**반환값**

set[str]: 부분 일치 검색에 사용할 두 글자 조각.

## `relevance_score`

[소스 선언 위치](../../../../../app/dialogue/preprocess_agent/retriever.py#L87)

```python
def relevance_score(question: str, fact: Fact) -> float:
    ...
```

명시적 ID·단어·두 글자 중복으로 관련성을 계산한다. 유사도가 사실 검증을 대신하지 않는다.

**파라미터**

- question (str): 사용자가 입력한 질문 원문.
- fact (Fact): 관련성을 계산할 승인 사실.

**반환값**

float: 질문과 승인 사실의 단어·부분 일치 점수.

## `retrieve_approved_facts`

[소스 선언 위치](../../../../../app/dialogue/preprocess_agent/retriever.py#L110)

```python
def retrieve_approved_facts(
    request: CharacterReplyRequest,
    top_k: int = 3,
    enabled: bool = True,
) -> RetrievalContext:
    ...
```

승인 범위 안에서 검색하고 필수 사실을 합친다. 입력 요청과 승인 원문은 수정하지 않는다.

top_k는 선택적 사실의 상한이다. 필수 사실 전체는 항상 포함한다. 하나의 사실에
함께 적힌 부정·시각·관찰 한계는 문장 일부로 자르지 않는다. 문맥이 너무 길면
기존 모델 입력 토큰 검사에서 명시적으로 거절하며 필수 사실을 조용히 삭제하지 않는다.

**파라미터**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- top_k (int): 추가로 선택할 관련 선택적 사실의 최대 개수. 필수 사실은 별도 보존한다.
- enabled (bool): 승인 사실의 관련성 검색을 수행할지 여부.

**반환값**

RetrievalContext: 필수 사실과 관련 선택적 사실을 원래 순서대로 담은 검색 결과.
