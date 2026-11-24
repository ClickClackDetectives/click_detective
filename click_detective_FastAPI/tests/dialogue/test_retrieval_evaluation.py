"""검색 평가의 계산과 공개 범위 사용을 확인한다."""

import pytest

from scripts.evaluate_retrieval import DEFAULT_DATASET, ROOT, evaluate, load_cases
from scripts.retrieval_metrics import measure, summarize


def test_retrieval_metrics_measure_ranking_and_rejection_separately():
    """잘못 고른 후보, 빠진 정답, 근거 없는 질문을 각각 계산한다.

    Args:
        없음.
    Returns:
        None: 순위와 실제 선택을 섞어 집계하지 않는지 검증한다.
    """
    cases = [
        {"id": "positive", "expected_fact_ids": ["a", "b"]},
        {"id": "negative", "expected_fact_ids": []},
    ]
    rankings = {
        "positive": [("wrong", 0.82), ("a", 0.80), ("b", 0.78)],
        "negative": [("wrong", 0.76)],
    }
    metrics = summarize(measure(cases, rankings, top_k=2, minimum_score=0.79))
    assert metrics["hit_at_1"] == 0
    assert metrics["recall_at_k"] == pytest.approx(0.5)
    assert metrics["mrr_at_k"] == pytest.approx(0.5)
    assert metrics["selection_precision"] == pytest.approx(0.5)
    assert metrics["answerable_exact_set_rate"] == 0
    assert metrics["false_match_rate"] == 0


def test_calibration_does_not_use_held_out_errors():
    """최종 평가의 오탐을 보고 기준점을 다시 조정하지 않는다.

    Args:
        없음.
    Returns:
        None: 기준 조정 세트와 최종 평가 결과를 확인한다.
    """
    cases = [
        {"id": "cal-pos", "split": "calibration", "expected_fact_ids": ["a"]},
        {"id": "cal-neg", "split": "calibration", "expected_fact_ids": []},
        {"id": "test-neg", "split": "test", "kind": "locked", "expected_fact_ids": []},
    ]
    rankings = {
        "cal-pos": [("a", 0.8)],
        "cal-neg": [("wrong", 0.7)],
        "test-neg": [("wrong", 0.9)],
    }
    report = evaluate(cases, rankings, top_k=1)
    assert report["minimum_score"] == 0.8
    assert report["calibration"]["false_match_rate"] == 0
    assert report["test"]["false_match_rate"] == 1


def test_dataset_gates_candidates_on_revealed_evidence():
    """같은 질문이 증거 공개 여부에 따라 다른 검색 범위를 갖는지 확인한다.

    Args:
        없음.
    Returns:
        None: 실제 사건 데이터의 인정 진술이 열리는 시점을 검증한다.
    """
    cases, documents = load_cases(DEFAULT_DATASET, ROOT / "data")
    indexed = {case["id"]: case for case in cases}
    before = indexed["kang-sleeping-pill-before-1"]
    after = indexed["kang-sleeping-pill-after-1"]
    assert before["question"] == after["question"]
    assert before["expected_fact_ids"] == []
    fact_id = "kang-admit-gang_drug"
    assert after["expected_fact_ids"] == [fact_id]
    assert fact_id not in documents[before["id"]]
    assert fact_id in documents[after["id"]]
