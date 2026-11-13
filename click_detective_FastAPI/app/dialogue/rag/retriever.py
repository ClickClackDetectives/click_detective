"""허용된 작은 사실 집합을 대상으로 하는 키워드 RAG.

첫 도입은 벡터 DB나 새 모델 없이 시작한다. 승인하지 않은 대본·정답·다른 수사의
기록은 검색하지 않는다. 검색 점수는 관련성 힌트이며 공개 권한·진실 판정이 아니다.
"""

from dataclasses import dataclass
import re
import unicodedata

from ..schemas import CharacterReplyRequest, Fact


@dataclass(frozen=True)
class RetrievedFact:
    """선택 이유와 출처를 보관하는 서버 내부 검색 항목. 원본 파일 출처로 가장하지 않는다."""

    fact_id: str
    score: float
    reason: str
    source_ref: str


@dataclass(frozen=True)
class RetrievalContext:
    """한 요청에서만 사용하는 검색 결과. 필수 사실은 top_k와 관계없이 보존한다."""

    game_id: str
    case_id: str
    scenario_version: str
    suspect_id: str
    selected_facts: tuple[Fact, ...]
    hits: tuple[RetrievedFact, ...]


def _terms(text: str) -> set[str]:
    """표기를 통일한 단어를 얻는다. 한국어 형태소 분석이나 의미 추론은 수행하지 않는다."""
    normalized = unicodedata.normalize("NFC", text).casefold()
    return set(re.findall(r"[가-힣a-z0-9]+", normalized))


def _bigrams(terms: set[str]) -> set[str]:
    """조사가 붙은 한국어 단어의 부분 일치를 위해 두 글자 조각을 만든다."""
    return {term[index:index + 2] for term in terms for index in range(len(term) - 1)}


def relevance_score(question: str, fact: Fact) -> float:
    """명시적 ID·단어·두 글자 중복으로 관련성을 계산한다. 유사도가 사실 검증을 대신하지 않는다."""
    query_terms = _terms(question)
    fact_terms = _terms(fact.text)
    query_parts = _bigrams(query_terms)
    shared_parts = query_parts & _bigrams(fact_terms)
    id_match = 10.0 if fact.id.casefold() in question.casefold() else 0.0
    word_match = float(len(query_terms & fact_terms))
    partial_match = len(shared_parts) / max(len(query_parts), 1)
    return id_match + word_match + partial_match


def retrieve_approved_facts(
    request: CharacterReplyRequest, top_k: int = 3, enabled: bool = True,
) -> RetrievalContext:
    """승인 범위 안에서 검색하고 필수 사실을 합친다. 입력 요청과 승인 원문은 수정하지 않는다.

    top_k는 선택적 사실의 상한이다. 필수 사실 전체는 항상 포함한다. 하나의 사실에
    함께 적힌 부정·시각·관찰 한계는 문장 일부로 자르지 않는다. 문맥이 너무 길면
    기존 모델 입력 토큰 검사에서 명시적으로 거절하며 필수 사실을 조용히 삭제하지 않는다.
    """
    if not 0 <= top_k <= 10:
        raise ValueError("RAG top_k must be between 0 and 10")
    approved = {fact.id: fact for fact in request.allowed_facts}
    required = set(request.required_fact_ids)
    if not required.issubset(approved):
        raise ValueError("Required facts must be approved")
    scores = {fact.id: relevance_score(request.question, fact) for fact in request.allowed_facts} if enabled else {}
    ranked_optional = sorted(
        (fact for fact in request.allowed_facts if fact.id not in required and scores.get(fact.id, 0) > 0),
        key=lambda fact: -scores[fact.id],
    )
    selected_ids = required | {fact.id for fact in ranked_optional[:top_k]}
    if not enabled:
        selected_ids = set(approved)
    # 문장 순서는 승인 계획 순서를 유지한다. 검색 순위 때문에 사실의 설명 순서를 뒤집지 않는다.
    selected = tuple(fact.model_copy(deep=True) for fact in request.allowed_facts if fact.id in selected_ids)
    hits = tuple(RetrievedFact(
        fact_id=fact.id, score=scores.get(fact.id, 0.0),
        reason="disabled" if not enabled else "required" if fact.id in required else "related",
        source_ref=f"request.allowed_facts/{fact.id}",
    ) for fact in selected)
    return RetrievalContext(
        game_id=request.game_id, case_id=request.case_id, scenario_version=request.scenario_version,
        suspect_id=request.suspect_id, selected_facts=selected, hits=hits,
    )
