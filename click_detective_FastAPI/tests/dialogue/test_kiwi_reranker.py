"""Kiwi BM25와 E5 검색의 병렬 실행 및 최종 진술 선택을 검사한다."""

from threading import Barrier

import pytest

from app.dialogue.services.preprocess_agent.rag import (
    dialogue_fact_retriever as question_search,
)
from app.dialogue.services.preprocess_agent.rag.dialogue_fact_retriever import (
    Candidate,
    QuestionSearch,
)


class FixedScores:
    """형태소 점수와 경쟁할 E5 점수를 고정한다.

    Args:
        없음.
    Returns:
        FixedScores: 질문과 진술의 유사도를 제공하는 대역 인덱스.
    """

    def score(self, question, texts):
        """테스트 진술의 고정 유사도를 반환한다.

        Args:
            question: 테스트에서 보낸 원문 질문.
            texts: 이번 요청에서 승인한 진술 텍스트.
        Returns:
            dict: 승인된 검색용 텍스트의 유사도.
        """
        scores = {
            "서재에서 대화를 나눴습니다.": 0.850,
            "식당에서 위스키를 마셨고 집사가 잔을 채워줬습니다.": 0.847,
            "위스키 잔을 채운 두 번째 손님의 이름, 직업, 신원을 모릅니다.": 0.830,
            question_search.OFF_TOPIC: 0.800,
        }
        return {text: scores[text] for text in texts}


async def test_kiwi_bm25_combines_independent_search_results(monkeypatch):
    """BM25가 E5 하한 미만의 진술을 독립 검색으로 찾는지 확인한다.

    Args:
        monkeypatch: 테스트 전용 공개 진술 후보를 주입한다.
    Returns:
        None: 순위 결합, 병렬 실행 및 최종 top_k 적용을 확인한다.
    """
    pytest.importorskip("bm25s")
    pytest.importorskip("kiwipiepy")
    from app.dialogue.services.preprocess_agent.rag.dialogue_kiwi_reranker import (
        KiwiBM25Reranker,
    )
    from app.runtime.runtime_settings import Settings

    candidates = [
        Candidate("서재에서 대화를 나눴습니다.", ({"key": "meeting"},)),
        Candidate(
            "식당에서 위스키를 마셨고 집사가 잔을 채워줬습니다.", ({"key": "dining"},)
        ),
        Candidate(
            "위스키 잔을 채운 두 번째 손님의 이름, 직업, 신원을 모릅니다.",
            ({"key": "below-floor"},),
        ),
        Candidate(question_search.OFF_TOPIC, ()),
    ]
    monkeypatch.setattr(question_search, "public_candidates", lambda *_: candidates)
    settings = Settings(
        _env_file=None,
        api_key="kiwi-regression-test-only",
        rag_top_k=1,
        rag_min_score=0.8322,
        rag_dense_weight=0.65,
    )
    query = "식당에서위스키잔을누가채워줬죠"
    assert settings.rag_rrf_k == 40
    index = FixedScores()
    dense = QuestionSearch(None, settings, index)
    reranker = KiwiBM25Reranker(settings.rag_dense_weight, settings.rag_rrf_k)
    hybrid = QuestionSearch(None, settings, index, reranker)
    assert dense.select(query, "yoon", []) == ([{"key": "meeting"}], None)
    assert hybrid.select(query, "yoon", []) == ([{"key": "dining"}], None)
    assert hybrid.select("🧩", "yoon", []) == dense.select("🧩", "yoon", [])

    barrier = Barrier(2, timeout=3)
    dense_score = index.score
    sparse_score = reranker.scores

    def score_in_parallel(question, texts):
        """BM25 검색이 시작된 후 E5 점수를 반환한다.

        Args:
            question: 원문 질문.
            texts: 공개된 진술의 검색용 텍스트.
        Returns:
            dict: 고정 E5 점수.
        """
        barrier.wait()
        return dense_score(question, texts)

    def bm25_in_parallel(question, texts):
        """E5 검색이 시작된 후 BM25 점수를 계산한다.

        Args:
            question: 원문 질문.
            texts: 공개된 개별 진술의 검색용 텍스트.
        Returns:
            dict: Kiwi 형태소를 사용한 BM25 점수.
        """
        barrier.wait()
        return sparse_score(question, texts)

    monkeypatch.setattr(index, "score", score_in_parallel)
    monkeypatch.setattr(reranker, "scores", bm25_in_parallel)
    query = "두 번째 손님의 이름, 직업, 신원을 모릅니까?"
    selected = await hybrid._select_parallel(query, "yoon", [])
    assert selected == ([{"key": "below-floor"}], None)
