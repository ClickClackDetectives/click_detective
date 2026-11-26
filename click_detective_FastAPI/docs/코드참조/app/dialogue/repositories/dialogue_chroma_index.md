# `app/dialogue/repositories/dialogue_chroma_index.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/dialogue/repositories/dialogue_chroma_index.py)

공개 진술의 E5 벡터를 ChromaDB 코사인 인덱스로 검색한다.

## `ChromaIndex`

[소스 선언](../../../../../app/dialogue/repositories/dialogue_chroma_index.py#L13)

```python
class ChromaIndex:
    ...
```

FastAPI 앱 하나에 속한 메모리 컬렉션을 관리한다.

**인자**

- encoder: 질문과 진술을 E5 벡터로 변환하는 인코더.
**반환값**

- ChromaIndex: 현재 요청에 승인된 문장만 검색하는 인덱스.

## `ChromaIndex.__init__`

[소스 선언](../../../../../app/dialogue/repositories/dialogue_chroma_index.py#L22)

```python
def __init__(self, encoder):
    ...
```

직접 받은 E5 벡터를 사용하는 코사인 컬렉션을 만든다.

**인자**

- encoder: 질문과 진술의 임베딩 모델.
**반환값**

- None: 앱 시작 시 사용할 컬렉션을 초기화한다.

## `ChromaIndex.close`

[소스 선언](../../../../../app/dialogue/repositories/dialogue_chroma_index.py#L42)

```python
def close(self):
    ...
```

앱이 종료될 때 해당 앱의 컬렉션을 제거한다.

**인자**

- 없음.
**반환값**

- None: 공유 로컬 클라이언트에서 이 컬렉션만 제거한다.

## `ChromaIndex.score`

[소스 선언](../../../../../app/dialogue/repositories/dialogue_chroma_index.py#L52)

```python
def score(self, question, texts):
    ...
```

요청에서 허용된 벡터만 검색하고 거리에서 유사도를 계산한다.

**인자**

- question: 플레이어가 입력한 질문.
- texts: 현재 인물과 공개 상태에서 승인된 검색용 문장.
**반환값**

- dict[str, float]: 문장별 코사인 유사도.

## `ChromaIndex._query_distances`

[소스 선언](../../../../../app/dialogue/repositories/dialogue_chroma_index.py#L93)

```python
def _query_distances(self, query, ids):
    ...
```

ChromaDB가 반환한 코사인 거리를 요청 ID 범위에서 읽는다.

**인자**

- query: 질문의 E5 벡터 배치.
- ids: 이 조회에서 허용된 진술 ID.
**반환값**

- dict[str, float]: ChromaDB가 반환한 ID와 코사인 거리.

## `ChromaIndex._read_missing_distances`

[소스 선언](../../../../../app/dialogue/repositories/dialogue_chroma_index.py#L118)

```python
def _read_missing_distances(self, query, ids):
    ...
```

근사 검색에서 누락된 승인 벡터만 읽어 코사인 거리를 계산한다.

**인자**

- query: 질문 하나의 E5 벡터.
- ids: 두 번의 Chroma 검색에서 반환되지 않은 승인 진술 ID.
**반환값**

- dict[str, float]: 누락됐던 승인 진술의 코사인 거리.
