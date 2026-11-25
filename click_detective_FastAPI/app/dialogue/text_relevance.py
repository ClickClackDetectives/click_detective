"""검증과 검색 평가가 공통으로 사용하는 키워드 관련성 점수."""

import re
import unicodedata


def _terms(text: str) -> set[str]:
    """표기를 통일한 단어를 추출한다.

    Args:
        text: 검색할 문장의 원문.

    Returns:
        set[str]: 정규화한 검색 단어.
    """
    normalized = unicodedata.normalize("NFC", text).casefold()
    return set(re.findall(r"[가-힣a-z0-9]+", normalized))


def _bigrams(terms: set[str]) -> set[str]:
    """조사가 붙은 단어의 부분 일치에 사용할 두 글자 조각을 얻는다.

    Args:
        terms: 정규화한 단어 집합.

    Returns:
        set[str]: 각 단어 안의 두 글자 조각.
    """
    result = set()
    for term in terms:
        for index in range(len(term) - 1):
            result.add(term[index : index + 2])
    return result


def text_relevance(question: str, fact_id: str, text: str) -> float:
    """팀 원본과 같은 ID·단어·두 글자 중복 점수를 계산한다.

    Args:
        question: 플레이어가 입력한 질문 원문.
        fact_id: 사실 또는 진술의 식별자.
        text: 검색용 진술 텍스트.

    Returns:
        float: ID 일치, 단어 일치와 부분 일치의 합.
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
