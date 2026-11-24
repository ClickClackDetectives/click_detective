"""진술 검색의 순위와 관련성 기준 적용 결과를 평가한다."""

from math import inf, nextafter
from statistics import mean


def measure(cases, rankings, top_k, minimum_score):
    """순위를 계산하고 관련성 기준을 적용한 결과를 함께 기록한다.

    Args:
        cases: 정답 진술 ID와 질문 유형을 담은 문항.
        rankings: 문항 ID별로 점수 내림차순으로 정렬한 (진술 ID, 점수).
        top_k: 실제 선택할 수 있는 최대 진술 수.
        minimum_score: 진술을 반환할 수 있는 최소 관련성 점수.
    Returns:
        list[dict]: 검색 순위, 선택된 ID와 문항별 평가 결과.
    """
    rows = []
    for case in cases:
        ranked = rankings[case["id"]]
        gold = set(case["expected_fact_ids"])
        selected = [
            fact_id for fact_id, score in ranked[:top_k] if score >= minimum_score
        ]
        positions = [
            position
            for position, (fact_id, _) in enumerate(ranked[:top_k], 1)
            if fact_id in gold
        ]
        rows.append(
            {
                **case,
                "ranked": [
                    {"id": fact_id, "score": score} for fact_id, score in ranked
                ],
                "selected_fact_ids": selected,
                "hit_at_1": bool(positions and positions[0] == 1) if gold else None,
                "recall_at_k": len(positions) / len(gold) if gold else None,
                "reciprocal_rank_at_k": (1 / positions[0] if positions else 0.0)
                if gold
                else None,
                "correct_selection_count": len(gold.intersection(selected)),
                "exact_set_match": set(selected) == gold,
            }
        )
    return rows


def summarize(rows):
    """정답이 있는 질문과 근거가 없는 질문의 결과를 각각 집계한다.

    Args:
        rows: 같은 설정으로 평가한 문항 결과 목록.
    Returns:
        dict: 순위 관련 지표, 선택 정밀도와 오탐률. 해당 문항이 없으면 None.
    """
    answerable = [row for row in rows if row["expected_fact_ids"]]
    unanswerable = [row for row in rows if not row["expected_fact_ids"]]
    count_selected = sum(len(row["selected_fact_ids"]) for row in rows)
    correct_selected = sum(row["correct_selection_count"] for row in rows)
    return {
        "questions": len(rows),
        "answerable": len(answerable),
        "unanswerable": len(unanswerable),
        "hit_at_1": mean(row["hit_at_1"] for row in answerable) if answerable else None,
        "recall_at_k": (
            mean(row["recall_at_k"] for row in answerable) if answerable else None
        ),
        "mrr_at_k": (
            mean(row["reciprocal_rank_at_k"] for row in answerable)
            if answerable
            else None
        ),
        "selection_precision": (
            correct_selected / count_selected if count_selected else None
        ),
        "answerable_exact_set_rate": (
            mean(row["exact_set_match"] for row in answerable) if answerable else None
        ),
        "false_match_rate": (
            mean(bool(row["selected_fact_ids"]) for row in unanswerable)
            if unanswerable
            else None
        ),
    }


def calibrate(cases, rankings, top_k):
    """정답 문항의 정확 선택률과 근거 없는 문항의 거절률을 균등하게 최적화한다.

    Args:
        cases: 기준 조정용 문항만 담은 목록.
        rankings: 문항별 검색 결과.
        top_k: 선택 진술 수의 상한.
    Returns:
        float: 검증 세트에 그대로 적용할 기준점. 동률이면 높은 기준을 사용한다.
    """
    if not any(row["expected_fact_ids"] for row in cases) or all(
        row["expected_fact_ids"] for row in cases
    ):
        raise ValueError("Calibration requires answerable and unanswerable questions.")

    scores = {score for case in cases for _, score in rankings[case["id"]][:top_k]} or {
        0.0
    }
    thresholds = sorted(scores | {nextafter(max(scores), inf)})
    best_threshold = thresholds[0]
    best_objective = -1.0
    for threshold in thresholds:
        metrics = summarize(measure(cases, rankings, top_k, threshold))
        objective = (
            metrics["answerable_exact_set_rate"] + 1 - metrics["false_match_rate"]
        ) / 2
        if objective >= best_objective:
            best_threshold = threshold
            best_objective = objective
    return best_threshold
