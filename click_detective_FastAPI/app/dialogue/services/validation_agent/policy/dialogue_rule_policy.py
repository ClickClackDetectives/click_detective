"""검증 정책에서 먼저 적용하는 결정적 문장 대조를 제공한다."""

from app.dialogue.services.validation_agent.evidence.dialogue_rules import (
    NEUTRAL_PROMPTS,
    normalize,
    rule_match,
)
from app.dialogue.services.validation_agent.sentences.dialogue_semantic_verification import (
    candidate_sentences,
)


class RulePolicy:
    """공개 범위와 승인 사실을 결정적으로 대조한다.

    Args:
        없음.

    Returns:
        RulePolicy: 생성형 모델을 호출하지 않는 검증 정책.
    """

    async def public_allowed(self, question, reply, sources):
        """공개 문구 또는 이전 발언으로 확인되는 문장만 남긴다.

        Args:
            question: 플레이어 질문.
            reply: 검사할 후보 대사.
            sources: 현재 인물의 공개 진술.

        Returns:
            bool: 모든 문장을 공개 범위에서 확인할 수 있는지 여부.
        """
        neutral = {normalize(text) for text in NEUTRAL_PROMPTS}
        return all(
            normalize(part.text) in neutral
            or any(rule_match(source, part.text) for source in sources)
            for part in candidate_sentences(reply)
        )

    async def supported_units(self, request, sentences, units, eligible):
        """후보 문장별로 승인 단위를 확실히 뒷받침하는 근거를 찾는다.

        Args:
            request: 현재 심문 요청.
            sentences: 재검증할 원본 후보 문장 목록.
            units: 승인 사실별 검증 단위.
            eligible: 후보 문장마다 유사도 기준을 통과한 단위 번호.

        Returns:
            dict: 유지할 문장 번호와 그 문장이 확인한 승인 단위 번호.
        """
        return {
            part.id: matches
            for part in sentences
            if (
                matches := {
                    index
                    for index in eligible[part.id]
                    if rule_match(units[index].text, part.text)
                }
            )
        }
