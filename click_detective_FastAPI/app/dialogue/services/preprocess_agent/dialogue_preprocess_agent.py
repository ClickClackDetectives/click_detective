"""PreprocessAgent의 처리 순서를 담는다."""

from time import perf_counter

from fastapi import HTTPException

from app.dialogue.dto.dialogue_graph_state import InterrogationState
from app.dialogue.dto.dialogue_reply_dto import CharacterReplyRequest
from app.dialogue.services.diagnostics.dialogue_diagnostics import trace_event
from app.dialogue.services.preprocess_agent.dialogue_preprocess_prompt import (
    build_messages,
)
from app.dialogue.services.validation_agent.sentences.dialogue_verification_units import (
    build_verification_units,
)


class PreprocessAgent:
    """질문과 승인 사실을 정리한다.

    Args:
        settings: 생성 프롬프트에 사용할 설정.
        question_search: 게임 심문의 승인 진술을 검색하는 객체 또는 None.

    Returns:
        PreprocessAgent: 해당 단계의 작업을 수행하는 객체.
    """

    def __init__(self, settings, question_search=None):
        """사용할 의존성과 초기 상태를 준비한다.

        Args:
            settings: 생성 프롬프트에 사용할 설정.
            question_search: 게임 심문에 사용할 진술 검색기 또는 None.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.settings = settings
        self.question_search = question_search

    async def preprocess_agent(self, state: InterrogationState) -> dict:
        """게임의 공개 범위에서 진술을 검색하고 생성 문맥을 만든다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

        Returns:
            dict: 최종 승인 요청, 프롬프트, 검증 문장 목록, 초기 생성 횟수와 검색 결과가 비었는지 여부.
        """
        request = state["request"]
        started = perf_counter()
        turn = state.get("search_turn")
        if turn is not None:
            plan, _ = await self.question_search.refine(turn.plan, turn.revealed)
            if plan is not turn.plan:
                request = CharacterReplyRequest.model_validate(
                    {
                        **request.model_dump(),
                        "topic_id": plan.topic,
                        "allowed_facts": plan.facts,
                        "required_fact_ids": [fact["id"] for fact in plan.facts],
                    }
                )
                turn.plan = plan
                turn.request = request
            turn.search_complete = True
        units = build_verification_units(request)
        if len(units) > 256:
            raise HTTPException(
                422, "Approved context contains too many verification sentences"
            )
        messages = build_messages(request, self.settings, units=units)
        trace_event(
            "preprocess",
            elapsed_ms=round((perf_counter() - started) * 1000, 2),
            approved_count=len(request.allowed_facts),
            required_count=len(request.required_fact_ids),
            unit_count=len(units),
        )
        return {
            "request": request,
            "messages": messages,
            "verification_units": units,
        }
