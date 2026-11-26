"""Kiwi BM25로 승인된 개별 진술을 검색하고 E5 순위와 결합한다."""

from functools import lru_cache
from threading import Lock
from unicodedata import normalize

from bm25s import BM25
from kiwipiepy import Kiwi

CONTENT_TAGS = frozenset({"NNG", "NNP", "NR", "VV", "VA", "MAG", "SL", "SN", "XR"})
MIN_BM25_SCORE = 1.25


class KiwiBM25Reranker:
    """현재 요청에서 공개 가능한 개별 진술로 BM25 인덱스를 만든다.

    Args:
        dense_weight: RRF에서 E5 순위에 줄 가중치.
        rank_constant: 순위 분모에 더하는 RRF 상수.
    Returns:
        KiwiBM25Reranker: E5가 고른 후보에 BM25 후보를 합치는 검색기.
    """

    def __init__(self, dense_weight, rank_constant):
        """형태소 분석기와 공개 진술 인덱스 캐시를 준비한다.

        Args:
            dense_weight: E5 순위의 가중치. BM25 가중치는 1에서 이 값을 뺀다.
            rank_constant: RRF의 순위 상수.
        Returns:
            None: 서버가 공유할 재정렬기의 상태를 초기화한다.
        """
        self._kiwi = Kiwi(num_workers=1)
        self._lock = Lock()
        self._corpus = lru_cache(maxsize=128)(self._build_corpus)
        self._dense_weight = dense_weight
        self._rank_constant = rank_constant

    def terms(self, text):
        """검색에 사용할 내용어의 형태소를 추출한다.

        Args:
            text: 질문 또는 검색용 진술 텍스트.
        Returns:
            list[str]: 품사 필터를 통과한 형태소.
        """
        return [
            token.form.casefold()
            for token in self._kiwi.tokenize(
                normalize("NFKC", text), normalize_coda=True
            )
            if token.tag.split("-", 1)[0] in CONTENT_TAGS
        ]

    def _build_corpus(self, texts):
        """공개 가능한 진술 집합의 BM25 점수를 준비한다.

        Args:
            texts: 현재 수사 상태에 허용된 중복 없는 검색용 진술 텍스트.
        Returns:
            BM25: 해당 진술 집합의 Lucene 방식 BM25 인덱스.
        """
        index = BM25(method="lucene", k1=1.2, b=0.75)
        index.index([self.terms(text) for text in texts], show_progress=False)
        return index

    def scores(self, question, documents):
        """공개된 개별 진술의 BM25 점수를 구한다.

        Args:
            question: 플레이어가 입력한 원문.
            documents: 중복 없는 개별 진술 텍스트.
        Returns:
            dict: 진술 텍스트별 BM25 점수.
        """
        if not documents or self._dense_weight == 1:
            return {}
        with self._lock:
            query = sorted(set(self.terms(question)))
            if not query:
                return {}
            scores = self._corpus(documents).get_scores(query)
        return dict(zip(documents, scores, strict=True))

    def fuse(self, ranked, dense_pool, scores):
        """BM25 상위 진술을 후보에 추가하고 가중 RRF로 정렬한다.

        Args:
            ranked: 시각 조건을 통과한 개별 진술 텍스트의 E5 순서 목록.
            dense_pool: E5 유사도 하한과 1위 점수 차이를 통과한 인덱스.
            scores: 전체 개별 진술의 BM25 점수.
        Returns:
            list[int]: 두 검색 후보를 합친 뒤 RRF로 정렬한 인덱스.
        """
        if not scores:
            return dense_pool
        sparse = sorted(
            (i for i, text in enumerate(ranked) if scores[text] > 0),
            key=lambda i: scores[ranked[i]],
            reverse=True,
        )
        pool = set(dense_pool)
        if sparse and scores[ranked[sparse[0]]] >= MIN_BM25_SCORE:
            pool.add(sparse[0])
        sparse_ranks = {index: rank for rank, index in enumerate(sparse, 1)}
        k = self._rank_constant
        weight = self._dense_weight
        fused = {
            index: weight / (k + index + 1)
            + ((1 - weight) / (k + sparse_ranks[index]) if index in sparse_ranks else 0)
            for index in pool
        }
        return sorted(pool, key=lambda i: (-fused[i], i))
