"""전처리 → 생성 → 검증의 연결과 전체 실행 시간을 관리한다."""

import asyncio
from time import perf_counter

from fastapi import HTTPException
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from app.dialogue.dto.dialogue_graph_state import InterrogationState, SearchTurn
from app.dialogue.dto.dialogue_reply_dto import (
    CharacterReplyRequest,
    CharacterReplyResponse,
)
from app.dialogue.services.diagnostics.dialogue_diagnostics import (
    finish_trace,
    start_trace,
    trace_agent_time,
)
from app.dialogue.services.inference_agent.dialogue_inference_agent import (
    InferenceAgent,
)
from app.dialogue.services.model.dialogue_local_model import ReplyModel
from app.dialogue.services.preprocess_agent.dialogue_preprocess_agent import (
    PreprocessAgent,
)
from app.dialogue.services.validation_agent.workflow.dialogue_validation_agent import (
    ValidationAgent,
    neutral_response,
)
from app.runtime.runtime_settings import Settings


class InterrogationGraph:
    """전처리·생성·검증의 실행 순서와 전체 시간 제한을 관리한다.

    Args:
        settings (Settings): 모델 실행과 검색에 사용할 설정.
        model (ReplyModel | None): 대사 생성과 검증에 사용할 모델. fixture에서는 None.
        question_search: 첫 노드에서 공개 진술을 찾는 검색기 또는 None.

    Returns:
        InterrogationGraph: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(
        self, settings: Settings, model: ReplyModel | None, question_search=None
    ) -> None:
        """한 모델을 생성·검증 호출에 공유한다. 검증자에게 생성자의 내부 추론은 전달하지 않는다.

        Args:
            settings (Settings): 모델 실행과 검색에 사용할 설정.
            model (ReplyModel | None): 대사 생성과 검증에 사용할 모델. fixture에서는 None.
            question_search: 첫 노드에서 공개 진술을 찾는 검색기 또는 None.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.settings = settings
        self.preprocessor = PreprocessAgent(settings, question_search)
        self.generator = InferenceAgent(settings, model)
        self.validator = None
        builder = StateGraph(InterrogationState, context_schema=asyncio.Timeout)
        builder.add_node("preprocess_agent", self.preprocess_agent)
        builder.add_node("inference_agent", self.inference_agent)
        builder.add_edge(START, "preprocess_agent")
        if model is None:
            builder.add_edge("preprocess_agent", "inference_agent")
            builder.add_edge("inference_agent", END)
        else:
            self.validator = ValidationAgent(settings, model)
            builder.add_node("validation_agent", self.validation_agent)
            builder.add_edge("preprocess_agent", "inference_agent")
            builder.add_edge("inference_agent", "validation_agent")
            builder.add_edge("validation_agent", END)
        self.graph = builder.compile()

    async def preprocess_agent(
        self, state: InterrogationState, runtime: Runtime[asyncio.Timeout]
    ) -> dict:
        """첫 노드에서 진술 검색과 프롬프트 구성을 수행한다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.
            runtime: 검색 뒤 시작할 생성·검증 제한 시간을 제공하는 그래프 실행 문맥.

        Returns:
            dict: 생성 프롬프트, 검증 단위와 초기 생성 횟수.
        """
        with trace_agent_time("preprocess_agent"):
            result = await self.preprocessor.preprocess_agent(state)
        deadline = runtime.context
        if deadline is not None and deadline.when() is None:
            deadline.reschedule(
                asyncio.get_running_loop().time() + self.settings.timeout_seconds
            )
        return result

    async def inference_agent(self, state: InterrogationState) -> dict:
        """생성 에이전트에 후보 대사 작성을 맡긴다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

        Returns:
            dict: 후보 대사와 시도 횟수 또는 실행 오류 상태.
        """
        with trace_agent_time("inference_agent"):
            return await self.generator.inference_agent(state)

    async def validation_agent(self, state: InterrogationState) -> dict:
        """검증 에이전트에 후보 대사의 사실 검사를 맡긴다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

        Returns:
            dict: 최종 검증 응답.
        """
        with trace_agent_time("validation_agent"):
            return await self.validator.validation_agent(state)

    async def generate(
        self, request: CharacterReplyRequest, *, search_turn: SearchTurn | None = None
    ) -> CharacterReplyResponse:
        """그래프를 실행한다. 검색과 생성·검증에는 각각 제한 시간을 적용한다.

        Args:
            request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
            search_turn: 게임 규칙이 승인한 자유 질문 검색 정보 또는 None.

        Returns:
            CharacterReplyResponse: 검증을 통과한 응답 또는 시간 초과 시 중립 응답.
        """
        started = perf_counter()
        trace, token = start_trace(request, self.settings)
        initial: InterrogationState = {"request": request}
        if search_turn is not None:
            initial["search_turn"] = search_turn
        timeout = self.settings.timeout_seconds if search_turn is None else None
        try:
            try:
                async with asyncio.timeout(timeout) as deadline:
                    result = await self.graph.ainvoke(initial, context=deadline)
                response = result["response"]
            except TimeoutError:
                if search_turn is not None:
                    request = search_turn.request
                if self.validator is None:
                    raise HTTPException(504, "Generation timed out") from None
                response = neutral_response(request)
            trace["finish_reason"] = response.finish_reason
            trace["model_version"] = response.model_version
            return response
        except HTTPException as error:
            trace["http_status"] = error.status_code
            raise
        finally:
            finish_trace(trace, token, self.settings, started)
