"""PreprocessAgent의 처리 순서를 담는다."""

from time import perf_counter

from fastapi import HTTPException

from ..diagnostics import trace_event
from ..state import InterrogationState
from ..validation_agent.verification_units import build_verification_units
from .prompt import build_messages
from .rag.retriever import retrieve_approved_facts


class PreprocessAgent:
    """질문과 승인 사실을 정리한다.

    Args:
        settings: 검색과 생성 실행에 사용할 설정.

    Returns:
        PreprocessAgent: 해당 단계의 작업을 수행하는 객체.
    """

    def __init__(self, settings):
        """사용할 의존성과 초기 상태를 준비한다.

        Args:
            settings: 모델 실행과 검색에 사용할 설정.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.settings = settings

    async def preprocess_agent(self, state: InterrogationState) -> dict:
        """에이전트 1: 승인 사실 안에서 검색하고 필수 사실을 보존하여 문맥을 만든다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

        Returns:
            dict: 생성 프롬프트, 검색 결과와 초기 생성 횟수.
        """
        request = state["request"]
        units = build_verification_units(request)
        if len(units) > 256:
            raise HTTPException(
                422, "Approved context contains too many verification sentences"
            )
        started = perf_counter()
        retrieval = retrieve_approved_facts(
            request, self.settings.rag_top_k, self.settings.rag_enabled
        )
        elapsed_ms = round((perf_counter() - started) * 1000, 2)
        scores = [hit.score for hit in retrieval.hits if hit.reason == "related"]
        trace_event(
            "retrieval",
            elapsed_ms=elapsed_ms,
            relevance_mean=round(sum(scores) / len(scores), 4) if scores else None,
            relevance_max=round(max(scores), 4) if scores else None,
            approved_count=len(request.allowed_facts),
            selected_count=len(retrieval.selected_facts),
            required_count=len(request.required_fact_ids),
            unit_count=len(units),
        )
        return {
            "messages": build_messages(request, self.settings, retrieval),
            "retrieval": retrieval,
            "attempt": 0,
        }
