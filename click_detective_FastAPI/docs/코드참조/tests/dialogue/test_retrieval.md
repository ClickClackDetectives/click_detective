# `tests/dialogue/test_retrieval.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/dialogue/test_retrieval.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 83줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

쉬운 반복문으로 바꾼 검색이 필수 사실과 원래 순서를 유지하는지 검사한다.

## 함께 읽을 코드

- [app/dialogue/preprocess_agent/rag/retriever.py](../../app/dialogue/preprocess_agent/rag/retriever.md)
- [app/dialogue/schemas.py](../../app/dialogue/schemas.md)
- [tests/dialogue/test_verification_reports.py](test_verification_reports.md)

## `facts_request`

[소스 선언 위치](../../../../tests/dialogue/test_retrieval.py#L9)

```python
def facts_request(client):
    ...
```

점수가 다른 선택 사실과 점수가 없는 필수 사실을 준비한다.

**파라미터**

- client: 테스트 앱 클라이언트.

**반환값**

CharacterReplyRequest: 검색 순서와 필수 사실 보존을 확인할 요청.

## `test_retrieval_preserves_required_fact_and_stable_score_order`

[소스 선언 위치](../../../../tests/dialogue/test_retrieval.py#L34)

```python
def test_retrieval_preserves_required_fact_and_stable_score_order(client):
    ...
```

점수가 같으면 먼저 승인된 사실을 고르고 필수 사실은 점수와 무관하게 유지한다.

**파라미터**

- client: 검색 입력을 만들 테스트 앱 클라이언트.

**반환값**

None: 필수 사실과 동점 중 먼저 나온 선택 사실이 원래 순서로 반환되는지 검사한다.

## `test_zero_optional_limit_keeps_required_fact`

[소스 선언 위치](../../../../tests/dialogue/test_retrieval.py#L55)

```python
def test_zero_optional_limit_keeps_required_fact(client):
    ...
```

선택 사실 수가 0이어도 필수 사실을 삭제하지 않는다.

**파라미터**

- client: 테스트 앱 클라이언트.

**반환값**

None: 점수가 없는 필수 사실만 남는지 검사한다.

## `test_disabled_retrieval_keeps_every_approved_fact`

[소스 선언 위치](../../../../tests/dialogue/test_retrieval.py#L69)

```python
def test_disabled_retrieval_keeps_every_approved_fact(client):
    ...
```

검색을 끄면 관련성과 상관없이 승인된 사실 전체를 보존한다.

**파라미터**

- client: 테스트 앱 클라이언트.

**반환값**

None: 승인 원래 순서와 검색 비활성화 이유를 확인한다.
