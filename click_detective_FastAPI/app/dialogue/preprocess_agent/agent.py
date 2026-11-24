"""PreprocessAgent의 처리 순서를 담는다."""

from time import perf_counter

from fastapi import HTTPException

from ..diagnostics import trace_event
from ..state import InterrogationState
from ..validation_agent.verification_units import build_verification_units
from .prompt import build_messages


class PreprocessAgent:
    """질문과 승인 사실을 정리한다.

    Args:
        settings: 생성 프롬프트에 사용할 설정.

    Returns:
        PreprocessAgent: 해당 단계의 작업을 수행하는 객체.
    """

    def __init__(self, settings):
        """사용할 의존성과 초기 상태를 준비한다.

        Args:
            settings: 생성 프롬프트에 사용할 설정.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.settings = settings

    async def preprocess_agent(self, state: InterrogationState) -> dict:
        """승인된 사실과 검증 문장으로 생성 문맥을 만든다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

        Returns:
            dict: 생성 프롬프트와 초기 생성 횟수.
        """
        request = state["request"]
        started = perf_counter()
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
        return {"messages": messages, "attempt": 0}
