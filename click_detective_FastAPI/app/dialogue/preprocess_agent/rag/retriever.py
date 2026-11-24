"""허용된 작은 사실 집합을 대상으로 하는 키워드 RAG.

첫 도입은 벡터 DB나 새 모델 없이 시작한다. 승인하지 않은 대본·정답·다른 수사의
기록은 검색하지 않는다. 검색 점수는 관련성 힌트이며 공개 권한·진실 판정이 아니다.
"""

import re
import unicodedata
from dataclasses import dataclass

from ...schemas import CharacterReplyRequest, Fact


@dataclass(frozen=True)
class RetrievedFact:
    """선택 이유와 출처를 보관하는 서버 내부 검색 항목. 원본 파일 출처로 가장하지 않는다.

    Args:
        fact_id (str): 원래 승인 사실의 식별자.
        score (float): 질문과 사실의 관련성 점수.
        reason (str): 검색 결과가 선택된 이유.
        source_ref (str): 승인 사실 내 출처 참조.

    Returns:
        RetrievedFact: 위 역할을 수행하도록 생성된 객체.
    """

    fact_id: str
    score: float
    reason: str
    source_ref: str


@dataclass(frozen=True)
class RetrievalContext:
    """한 요청에서만 사용하는 검색 결과. 필수 사실은 top_k와 관계없이 보존한다.

    Args:
        game_id (str): 조회하거나 변경할 수사의 식별자.
        case_id (str): 조회하거나 생성할 사건의 식별자.
        scenario_version (str): 현재 사건 데이터의 스냅샷 버전.
        suspect_id (str): 심문 대상 인물의 식별자.
        selected_facts (tuple[Fact, ...]): 검색으로 선택한 승인 사실 목록.
        hits (tuple[RetrievedFact, ...]): 사실별 검색 점수와 선택 이유.

    Returns:
        RetrievalContext: 위 역할을 수행하도록 생성된 객체.
    """

    game_id: str
    case_id: str
    scenario_version: str
    suspect_id: str
    selected_facts: tuple[Fact, ...]
    hits: tuple[RetrievedFact, ...]


def _terms(text: str) -> set[str]:
    """표기를 통일한 단어를 얻는다. 한국어 형태소 분석이나 의미 추론은 수행하지 않는다.

    Args:
        text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

    Returns:
        set[str]: 표기와 대소문자를 정규화한 검색 단어.
    """
    normalized = unicodedata.normalize("NFC", text).casefold()
    return set(re.findall(r"[가-힣a-z0-9]+", normalized))


def _bigrams(terms: set[str]) -> set[str]:
    """조사가 붙은 한국어 단어의 부분 일치를 위해 두 글자 조각을 만든다.

    Args:
        terms (set[str]): 정규화한 검색 단어 집합.

    Returns:
        set[str]: 부분 일치 검색에 사용할 두 글자 조각.
    """
    result = set()
    for term in terms:
        for index in range(len(term) - 1):
            result.add(term[index : index + 2])
    return result


def relevance_score(question: str, fact: Fact) -> float:
    """명시적 ID·단어·두 글자 중복으로 관련성을 계산한다. 유사도가 사실 검증을 대신하지 않는다.

    Args:
        question (str): 사용자가 입력한 질문 원문.
        fact (Fact): 관련성을 계산할 승인 사실.

    Returns:
        float: 질문과 승인 사실의 단어·부분 일치 점수.
    """
    return text_relevance(question, fact.id, fact.text)


def text_relevance(question: str, fact_id: str, text: str) -> float:
    """진술 본문과 검색용 메타데이터의 문자 관련성을 계산한다.

    Args:
        question: 플레이어가 입력한 질문 원문.
        fact_id: 사실 또는 진술의 식별자.
        text: 검색할 원문 또는 메타데이터를 포함한 문자열.
    Returns:
        float: 완전 일치와 두 글자 부분 일치를 합친 점수.
    """
    query_terms = _terms(question)
    fact_terms = _terms(text)
    query_parts = _bigrams(query_terms)
    shared_parts = query_parts & _bigrams(fact_terms)
    if fact_id.casefold() in question.casefold():
        id_match = 10.0
    else:
        id_match = 0.0
    word_match = float(len(query_terms & fact_terms))
    partial_match = len(shared_parts) / max(len(query_parts), 1)
    return id_match + word_match + partial_match


def retrieve_approved_facts(
    request: CharacterReplyRequest,
    top_k: int = 3,
    enabled: bool = True,
) -> RetrievalContext:
    """승인 범위 안에서 검색하고 필수 사실을 합친다. 입력 요청과 승인 원문은 수정하지 않는다.

    top_k는 선택적 사실의 상한이다. 필수 사실 전체는 항상 포함한다. 하나의 사실에
    함께 적힌 부정·시각·관찰 한계는 문장 일부로 자르지 않는다. 문맥이 너무 길면
    기존 모델 입력 토큰 검사에서 명시적으로 거절하며 필수 사실을 조용히 삭제하지 않는다.

    Args:
        request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
        top_k (int): 추가로 선택할 관련 선택적 사실의 최대 개수. 필수 사실은 별도 보존한다.
        enabled (bool): 승인 사실의 관련성 검색을 수행할지 여부.

    Returns:
        RetrievalContext: 필수 사실과 관련 선택적 사실을 원래 순서대로 담은 검색 결과.
    """
    if top_k < 0 or top_k > 10:
        raise ValueError("RAG top_k must be between 0 and 10")

    approved = {}
    scores = {}
    required_ids = set(request.required_fact_ids)
    for fact in request.allowed_facts:
        approved[fact.id] = fact
        if enabled and fact.id not in required_ids:
            scores[fact.id] = relevance_score(request.question, fact)

    for fact_id in required_ids:
        if fact_id not in approved:
            raise ValueError("Required facts must be approved")

    # 필수 사실을 먼저 선택하고, 남은 사실은 점수가 높은 순서로 고른다.
    selected_ids = set(required_ids)
    ranked_ids = sorted(scores, key=scores.get, reverse=True)
    optional_count = 0
    for fact_id in ranked_ids:
        if optional_count >= top_k:
            break
        if scores[fact_id] <= 0:
            continue
        selected_ids.add(fact_id)
        optional_count += 1

    if not enabled:
        selected_ids = set(approved)

    # 최종 결과는 점수 순서가 아니라 원래 승인 사실의 순서로 만든다.
    selected_facts = []
    hits = []
    for fact in request.allowed_facts:
        if fact.id not in selected_ids:
            continue
        selected_facts.append(fact.model_copy(deep=True))
        if not enabled:
            reason = "disabled"
        elif fact.id in required_ids:
            reason = "required"
        else:
            reason = "related"
        hit = RetrievedFact(
            fact_id=fact.id,
            score=scores.get(fact.id, 0.0),
            reason=reason,
            source_ref="request.allowed_facts/" + fact.id,
        )
        hits.append(hit)

    return RetrievalContext(
        game_id=request.game_id,
        case_id=request.case_id,
        scenario_version=request.scenario_version,
        suspect_id=request.suspect_id,
        selected_facts=tuple(selected_facts),
        hits=tuple(hits),
    )
