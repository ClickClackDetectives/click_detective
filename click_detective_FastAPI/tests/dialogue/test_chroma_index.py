"""실제 Chroma 컬렉션의 요청별 ID 필터와 점수 변환을 검사한다."""

import pytest


class FixedEncoder:
    """외부 모델 파일 없이 코사인 값이 알려진 벡터를 반환한다.

    Args:
        없음.
    Returns:
        FixedEncoder: 인코딩한 진술 목록을 기록하는 인코더.
    """

    def __init__(self):
        """벡터와 진술 인코딩 기록을 준비한다.

        Args:
            없음.
        Returns:
            None: 진술과 질문 벡터를 초기화한다.
        """
        self.indexed = []
        self.vectors = {"공개": [0.8, 0.6], "인정": [1.0, 0.0], "질문": [1.0, 0.0]}

    def encode(self, texts, *, prefix):
        """요청한 문장 순서에 따라 고정 벡터를 반환한다.

        Args:
            texts: 벡터화할 질문 또는 진술.
            prefix: 질문과 진술을 구분하는 E5 접두어.
        Returns:
            list: 각 문장에 대응하는 단위 벡터.
        """
        if prefix == "passage: ":
            self.indexed.extend(texts)
        return [self.vectors[text] for text in texts]


def test_chroma_filters_already_indexed_testimony():
    """한 게임에 공개된 진술을 인덱싱한 후 다른 게임에서 제외한다.

    Args:
        없음.
    Returns:
        None: 점수 변환, 요청별 검색 범위, 벡터 재사용을 검사한다.
    """
    pytest.importorskip("chromadb.config")
    from app.dialogue.repositories.dialogue_chroma_index import ChromaIndex

    encoder = FixedEncoder()
    index = ChromaIndex(encoder)
    try:
        assert index.score("질문", ["공개", "인정", "공개"]) == pytest.approx(
            {"공개": 0.8, "인정": 1.0}, abs=1e-6
        )
        assert index.score("질문", ["공개"]) == pytest.approx({"공개": 0.8}, abs=1e-6)
        assert encoder.indexed == ["공개", "인정"]
    finally:
        index.close()


@pytest.mark.parametrize("retry_returns_vector", [True, False])
def test_chroma_retries_only_missing_ids(monkeypatch, retry_returns_vector):
    """근사 검색에서 일부 후보가 빠지면 해당 승인 ID만 다시 조회한다.

    Args:
        monkeypatch: 첫 조회에서 한 후보가 빠지는 상황을 만든다.
        retry_returns_vector: 두 번째 근사 검색이 누락 후보를 반환하는지 여부.
    Returns:
        None: 두 번째 조회의 범위와 최종 코사인 점수를 검증한다.
    """
    pytest.importorskip("chromadb.config")
    from app.dialogue.repositories.dialogue_chroma_index import ChromaIndex

    index = ChromaIndex(FixedEncoder())
    query = index._collection.query
    get = index._collection.get
    requests = []
    exact_reads = []

    def partial(**kwargs):
        """첫 응답에서 두 번째 요청 ID의 거리를 생략한다.

        Args:
            kwargs: Chroma 컬렉션 검색에 전달할 키워드 인수.
        Returns:
            dict: 호출 횟수에 따라 일부 또는 전체 검색 결과.
        """
        ids = kwargs["ids"]
        requests.append(ids)
        if len(requests) == 1:
            return query(**(kwargs | {"ids": ids[:1], "n_results": 1}))
        if not retry_returns_vector:
            return {"ids": [[]], "distances": [[]]}
        return query(**kwargs)

    def read(**kwargs):
        """정확 거리 계산에 사용한 벡터 조회를 기록한다.

        Args:
            kwargs: Chroma 벡터 조회에 전달할 키워드 인수.
        Returns:
            dict: 실제 Chroma에 저장된 승인 벡터.
        """
        exact_reads.append(kwargs["ids"])
        return get(**kwargs)

    try:
        monkeypatch.setattr(index._collection, "query", partial)
        monkeypatch.setattr(index._collection, "get", read)
        assert index.score("질문", ["공개", "인정"]) == pytest.approx(
            {"공개": 0.8, "인정": 1.0}, abs=1e-6
        )
        assert requests[1:] == [requests[0][1:]]
        assert exact_reads == ([] if retry_returns_vector else requests[1:])
    finally:
        index.close()
