"""InferenceAgent의 처리 순서를 담는다."""

import asyncio
from time import perf_counter

from fastapi import HTTPException

from app.dialogue.dto.dialogue_graph_state import InterrogationState
from app.dialogue.dto.dialogue_reply_dto import CharacterReplyResponse
from app.dialogue.services.diagnostics.dialogue_diagnostics import trace_event
from app.dialogue.services.model.dialogue_local_model import ModelContextError
from app.dialogue.services.reply.dialogue_reply_validation import assemble_reply


class InferenceAgent:
    """모델에 후보 대사 생성을 요청한다.

    Args:
        settings: 검색과 생성 실행에 사용할 설정.
        model: 대사 생성에 사용할 공용 모델. 전처리에서는 직접 호출하지 않는다.

    Returns:
        InferenceAgent: 해당 단계의 작업을 수행하는 객체.
    """

    def __init__(self, settings, model):
        """사용할 의존성과 초기 상태를 준비한다.

        Args:
            settings: 모델 실행과 검색에 사용할 설정.
            model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.settings = settings
        self.model = model

    async def inference_agent(self, state: InterrogationState) -> dict:
        """에이전트 2: 사실의 의미를 유지하며 표현을 샘플링한다. 원문 복사를 요구하지 않는다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

        Returns:
            dict: 후보 대사 또는 실행 오류 상태.
        """
        request = state["request"]
        if self.model is None:
            return {
                "response": CharacterReplyResponse(
                    request_id=request.request_id,
                    suspect_id=request.suspect_id,
                    state_revision=request.state_revision,
                    reply=assemble_reply(request),
                    used_fact_ids=[fact.id for fact in request.allowed_facts],
                    model_version="click-fixture-v1",
                    finish_reason="fixed",
                )
            }
        result = {"error_status": None}
        try:
            async with asyncio.timeout(self.settings.timeout_seconds):
                started = perf_counter()
                raw = await self.model.generate(
                    list(state["messages"]), purpose="dialogue"
                )
                trace_event(
                    "generation",
                    attempt=1,
                    elapsed_ms=round((perf_counter() - started) * 1000, 2),
                )
            result["raw_output"] = raw
            return result
        except ModelContextError:
            raise HTTPException(
                422, "Approved context exceeds local token budget"
            ) from None
        except TimeoutError:
            result["error_status"] = 504
            return result
        except (RuntimeError, ValueError):
            result["error_status"] = 502
            return result
