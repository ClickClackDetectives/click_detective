"""공개 진술의 검색 결과에 시각 조건과 최종 선택 기준을 적용한다."""

from app.dialogue.services.preprocess_agent.rag.dialogue_testimony_time import (
    exact_minute,
    fits_time,
)

MAX_SCORE_GAP = 0.02


def select_ranked(question, ranked, scores, settings, reranker):
    """E5로 관련성을 확인하고 두 검색의 개별 진술 후보를 합친다.

    Args:
        question: 플레이어가 입력한 원문.
        ranked: E5 점수가 높은 순으로 정렬한 전체 공개 후보.
        scores: 개별 진술별 BM25 점수.
        settings: 최소 유사도와 최종 진술 개수 설정.
        reranker: 가중 RRF로 순위를 결합하는 검색기.
    Returns:
        tuple | None: 최종 진술과 주제 또는 매칭 없음.
    """
    minute = exact_minute(question)
    eligible = [
        (score, candidate)
        for score, candidate in ranked
        if minute is None or not candidate.entries or fits_time(candidate, minute)
    ]
    best, first = eligible[0]  # 사건 외 비교 문장은 시각과 관계없이 남는다.
    if best < settings.rag_min_score or not first.entries:
        return None
    if first.topic:
        return list(first.entries), first.topic

    individual = [
        (score, hit) for score, hit in eligible if hit.entries and not hit.topic
    ]
    cutoff = max(settings.rag_min_score, best - MAX_SCORE_GAP)
    pool = [i for i, (score, _) in enumerate(individual) if score >= cutoff]
    if reranker is not None:
        pool = reranker.fuse([hit.text for _, hit in individual], pool, scores)
    selected = [
        entry for i in pool[: settings.rag_top_k] for entry in individual[i][1].entries
    ]
    topics = {entry.get("_topic") for entry in selected}
    return selected, topics.pop() if len(topics) == 1 else None
