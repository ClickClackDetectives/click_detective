"""승인 사실 검증의 문장 필터, 재검증과 부분 응답을 조정한다."""

import asyncio
from time import perf_counter

from app.dialogue.dto.dialogue_reply_dto import CharacterReplyResponse
from app.dialogue.services.diagnostics.dialogue_diagnostics import trace_event
from app.dialogue.services.text.dialogue_text_relevance import text_relevance
from app.dialogue.services.validation_agent.evidence.dialogue_rules import (
    SentenceTransformerSimilarity,
    public_sources,
    rule_match,
)
from app.dialogue.services.validation_agent.output.dialogue_neutral import (
    select_neutral_reply,
)
from app.dialogue.services.validation_agent.output.dialogue_output import ReplyOutput
from app.dialogue.services.validation_agent.policy.dialogue_validation_policy import (
    HybridPolicy,
)
from app.dialogue.services.validation_agent.sentences.dialogue_semantic_verification import (
    candidate_sentences,
)

NEUTRAL_MODEL = "fixed-neutral-v2"


def neutral_response(request):
    """승인 사실의 유무에 맞는 고정 대사를 반환한다.

    Args:
        request: 승인 범위와 응답 식별 정보를 가진 요청.

    Returns:
        CharacterReplyResponse: 승인 사실 전달을 기록하지 않는 중립 응답.
    """
    category, reply = select_neutral_reply(request)
    trace_event(
        "validation_outcome",
        neutral_category=category,
        code="filtered_reply_validation_failed"
        if request.allowed_facts
        else "no_approved_facts_out_of_scope",
        delivered_fact_ids=[],
        withheld_required_fact_ids=request.required_fact_ids,
    )
    return CharacterReplyResponse(
        request_id=request.request_id,
        suspect_id=request.suspect_id,
        state_revision=request.state_revision,
        reply=reply,
        used_fact_ids=[],
        model_version=NEUTRAL_MODEL,
        finish_reason="neutral",
    )


class ValidationAgent:
    """유사도 검사와 규칙·모델 판정으로 승인된 문장을 고른다.

    Args:
        settings: 유사도와 검증 조건을 지정한 설정.
        model: 검증 호출을 지원하는 로컬 모델.

    Returns:
        ValidationAgent: 전부·일부·중립 응답을 결정하는 검증 에이전트.
    """

    def __init__(self, settings, model):
        """판정 정책과 출력 파서를 준비한다.

        Args:
            settings: 검증 에이전트 설정.
            model: 서버가 로드한 모델.

        Returns:
            None: 에이전트의 실행 의존성을 저장한다.
        """
        self.settings = settings
        self.output = ReplyOutput(settings, model)
        self.embedding = SentenceTransformerSimilarity(
            settings.validation_embedding_model, settings.validation_embedding_device
        )
        self.policy = HybridPolicy(settings, model)

    async def validation_agent(self, state):
        """후보 대사를 검사하고 전부·일부·중립 중 하나로 종료한다.

        Args:
            state: 요청, 전처리 검증 단위, 후보 원문과 모델 오류를 담은 그래프 상태.

        Returns:
            dict: 승인된 최종 응답.
        """
        started = perf_counter()
        request = state["request"]
        try:
            if state.get("error_status") or not state.get("raw_output"):
                response = neutral_response(request)
            else:
                try:
                    candidate = self.output.parse(request, state["raw_output"])
                except (ValueError, TypeError):
                    candidate = None
                response = (
                    await self.verify(request, candidate, state["verification_units"])
                    if candidate is not None
                    else neutral_response(request)
                )
            return {"response": response}
        finally:
            trace_event(
                "verification_policy",
                elapsed_ms=round((perf_counter() - started) * 1000, 2),
            )

    async def verify(self, request, candidate, units):
        """공개 범위 검사 또는 세 단계 문장 검증을 수행한다.

        Args:
            request: 승인 사실과 현재 공개 문맥.
            candidate: 생성 모델이 반환한 대사.
            units: 생성 프롬프트를 구성할 때 사용한 승인 문장 단위.

        Returns:
            CharacterReplyResponse: 이번 판정의 최종 응답.
        """
        if not request.allowed_facts:
            sources = public_sources(request, self.settings.history_limit)
            if await self.policy.public_allowed(
                request.question, candidate.reply, sources
            ):
                return candidate
            return neutral_response(request)

        sentences = candidate_sentences(candidate.reply)
        if len(sentences) > 256:
            return neutral_response(request)
        eligible = await self.check_similarity(sentences, units)
        remaining = [part for part in sentences if eligible[part.id]]
        matches = await self.policy.supported_units(request, remaining, units, eligible)
        accepted_units = {index for indices in matches.values() for index in indices}
        fact_units = {}
        for index, unit in enumerate(units):
            fact_units.setdefault(unit.fact_id, []).append(index)
        used = []
        for fact in request.allowed_facts:
            indexes = fact_units.get(fact.id, [])
            core = request._finding_core_sentences.get(fact.id, ())
            if core:
                verified = any(
                    index in accepted_units
                    for position, index in enumerate(indexes)
                    if position in core
                )
            else:
                verified = bool(indexes) and all(
                    index in accepted_units for index in indexes
                )
            if verified:
                used.append(fact.id)
        required = set(request.required_fact_ids)
        if required and not required.intersection(used):
            return neutral_response(request)
        if not required and not any(
            text_relevance(request.question, fact.id, fact.text) > 0
            for fact in request.allowed_facts
            if fact.id in used
        ):
            return neutral_response(request)
        kept = [part.text for part in remaining if part.id in matches]
        if not kept:
            return neutral_response(request)

        missing = [
            fact_id for fact_id in request.required_fact_ids if fact_id not in used
        ]
        if missing:
            kept.append(
                "도착 시각은 지금 말씀드리기 어렵습니다."
                if len(missing) == 1
                and "도착 시각" in request.question
                and any(
                    "도착" in fact.text and fact.id == missing[0]
                    for fact in request.allowed_facts
                )
                else "나머지 부분은 지금 말씀드리기 어렵습니다."
            )
        reply = " ".join(kept)
        if len(reply) > 12000:
            return neutral_response(request)
        trace_event(
            "validation_outcome",
            code="partial_reply_missing_required_facts" if missing else "approved",
            delivered_fact_ids=used,
            withheld_required_fact_ids=missing,
        )
        response = candidate.model_copy(
            update={
                "reply": reply,
                "used_fact_ids": used,
                "finish_reason": "partial" if missing else "stop",
            }
        )
        for fact_id in used:
            if fact_id not in request._finding_core_sentences:
                continue
            indexes = set(fact_units[fact_id])
            response._verified_finding_excerpts[fact_id] = " ".join(
                part.text
                for part in remaining
                if indexes.intersection(matches.get(part.id, ()))
            )
        return response

    async def check_similarity(self, sentences, units):
        """대사 문장별로 유사도 기준을 만족하는 승인 단위를 고른다.

        Args:
            sentences: 원래 대사에 있는 문장 목록.
            units: 승인 사실을 분리한 검증 단위.

        Returns:
            dict: 문장 번호별 유사도 후보 목록.
        """
        candidates = [part.text for part in sentences]
        approved = [unit.text for unit in units]
        scores = await asyncio.to_thread(self.embedding.scores, candidates, approved)
        eligible = {}
        for part, row in zip(sentences, scores, strict=True):
            eligible[part.id] = [
                i
                for i, score in enumerate(row)
                if score >= self.settings.validation_similarity_threshold
                or rule_match(units[i].text, part.text)
            ]
        return eligible
