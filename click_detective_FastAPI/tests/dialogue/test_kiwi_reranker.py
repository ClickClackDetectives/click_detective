"""Kiwi BM25가 자유 질문의 E5 후보를 재정렬하는 동작을 검사한다."""

import pytest

from app.dialogue.preprocess_agent import question_search
from app.dialogue.preprocess_agent.question_search import Candidate, QuestionSearch


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
            "위스키 잔을 채운 두 번째 사람은 모릅니다.": 0.830,
            question_search.OFF_TOPIC: 0.800,
        }
        return {text: scores[text] for text in texts}


def test_kiwi_bm25_selects_only_from_e5_pool(monkeypatch):
    """형태소 단서가 가까운 E5 후보의 순서를 바꾸는지 확인한다.

    Args:
        monkeypatch: 테스트 전용 공개 진술 후보를 주입한다.
    Returns:
        None: 재정렬 결과와 유사도 하한·top_k 적용을 비교한다.
    """
    pytest.importorskip("bm25s")
    pytest.importorskip("kiwipiepy")
    from app.config import Settings
    from app.dialogue.preprocess_agent.kiwi_reranker import KiwiBM25Reranker

    candidates = [
        Candidate("서재에서 대화를 나눴습니다.", ({"key": "meeting"},)),
        Candidate(
            "식당에서 위스키를 마셨고 집사가 잔을 채워줬습니다.", ({"key": "dining"},)
        ),
        Candidate(
            "위스키 잔을 채운 두 번째 사람은 모릅니다.", ({"key": "below-floor"},)
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
