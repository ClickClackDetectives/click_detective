"""v2 검증의 문장 필터, 재검증과 부분 응답을 조정한다."""

import asyncio
from time import perf_counter

from ..diagnostics import trace_event
from ..preprocess_agent.rag.retriever import relevance_score
from ..schemas import CharacterReplyResponse
from ..validation_agent_v1.output import ReplyOutput
from ..validation_agent_v1.semantic_verification import candidate_sentences
from ..validation_agent_v1.verification_units import build_verification_units
from .rules import (
    NO_APPROVAL_REPLY,
    UNVERIFIED_REPLY,
    SentenceTransformerSimilarity,
    char_ngram_scores,
    public_sources,
    rule_match,
)
from .v2_1.policy import HybridPolicy
from .v2_2.policy import RulePolicy

NEUTRAL_MODEL = "fixed-neutral-v2"


def neutral_response(request):
    """승인 사실의 유무에 맞는 고정 대사를 반환한다.

    Args:
        request: 승인 범위와 응답 식별 정보를 가진 요청.

    Returns:
        CharacterReplyResponse: 승인 사실 전달을 기록하지 않는 중립 응답.
    """
    trace_event(
        "validation_outcome",
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
        reply=UNVERIFIED_REPLY if request.allowed_facts else NO_APPROVAL_REPLY,
        used_fact_ids=[],
        model_version=NEUTRAL_MODEL,
        finish_reason="neutral",
    )


class ValidationAgentV2:
    """공통 필터 흐름에 v2.1 또는 v2.2 판정 정책을 연결한다.

    Args:
        settings: 버전과 유사도 기준을 지정한 설정.
        model: 생성 모델 및 v2.1의 검증 실행기.

    Returns:
        ValidationAgentV2: 대사를 재생성하지 않는 검증 에이전트.
    """

    def __init__(self, settings, model):
        """선택한 버전의 판정 정책과 공통 출력 파서를 준비한다.

        Args:
            settings: 검증 에이전트 설정.
            model: 서버가 로드한 모델.

        Returns:
            None: 에이전트의 실행 의존성을 저장한다.
        """
        self.settings = settings
        self.output = ReplyOutput(settings, model)
        self.embedding = (
            SentenceTransformerSimilarity(
                settings.validation_embedding_model,
                settings.validation_embedding_device,
            )
            if settings.validation_similarity_backend == "sentence_transformer"
            else None
        )
        self.policy = (
            HybridPolicy(settings, model)
            if settings.validation_agent_version == "v2.1"
            else RulePolicy()
        )

    async def validation_agent(self, state):
        """후보 대사를 검사하고 전부·일부·중립 중 하나로 종료한다.

        Args:
            state: 요청, 후보 원문과 모델 오류를 담은 그래프 상태.

        Returns:
            dict: 응답과 재생성 금지 상태.
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
                    await self.verify(request, candidate)
                    if candidate is not None
                    else neutral_response(request)
                )
            return {"response": response, "retry": False}
        finally:
            trace_event(
                "verification_policy",
                version=self.settings.validation_agent_version,
                elapsed_ms=round((perf_counter() - started) * 1000, 2),
            )

    async def verify(self, request, candidate):
        """공개 범위 검사 또는 세 단계 문장 검증을 수행한다.

        Args:
            request: 승인 사실과 현재 공개 문맥.
            candidate: 생성 모델이 반환한 대사.

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

        units = build_verification_units(request)
        sentences = candidate_sentences(candidate.reply)
        if len(sentences) > 256:
            return neutral_response(request)
        eligible = await self.check_similarity(sentences, units)
        remaining = [part for part in sentences if eligible[part.id]]
        matches = await self.policy.supported_units(request, remaining, units, eligible)
        accepted_units = {index for indices in matches.values() for index in indices}
        used = [
            fact.id
            for fact in request.allowed_facts
            if all(
                index in accepted_units
                for index, unit in enumerate(units)
                if unit.fact_id == fact.id
            )
        ]
        required = set(request.required_fact_ids)
        if required and not required.intersection(used):
            return neutral_response(request)
        if not required and not any(
            relevance_score(request.question, fact) > 0
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
        return candidate.model_copy(
            update={
                "reply": reply,
                "used_fact_ids": used,
                "finish_reason": "partial" if missing else "stop",
            }
        )

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
        if self.embedding:
            scores = await asyncio.to_thread(
                self.embedding.scores, candidates, approved
            )
        else:
            scores = char_ngram_scores(candidates, approved)
        eligible = {}
        for part, row in zip(sentences, scores, strict=True):
            eligible[part.id] = [
                i
                for i, score in enumerate(row)
                if score >= self.settings.validation_similarity_threshold
                or rule_match(units[i].text, part.text)
            ]
        return eligible
