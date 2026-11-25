"""전처리 → 생성 → 검증의 연결과 전체 실행 시간을 관리한다."""

import asyncio
from time import perf_counter

from fastapi import HTTPException
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from ..config import Settings
from .diagnostics import finish_trace, start_trace, trace_agent_time
from .inference_agent.agent import InferenceAgent
from .local_model import ReplyModel
from .preprocess_agent.agent import PreprocessAgent
from .schemas import CharacterReplyRequest, CharacterReplyResponse
from .state import GeneratedReply as GeneratedReply
from .state import InterrogationState, SearchTurn
from .state import OutputRejected as OutputRejected
from .validation_agent_v1.agent import ValidationAgent
from .validation_agent_v1.evidence_checks import check_report_evidence
from .validation_agent_v2.agent import ValidationAgentV2, neutral_response
from .validation_agent_v2.neutral import classify_neutral_question


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
        self.model = model
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
            self.validator = (
                ValidationAgent(settings, model)
                if settings.validation_agent_version == "v1"
                else ValidationAgentV2(settings, model)
            )
            builder.add_node("validation_agent", self.validation_agent)
            builder.add_conditional_edges(
                "preprocess_agent",
                self.after_preprocess,
                {"generate": "inference_agent", "validate": "validation_agent"},
            )
            builder.add_edge("inference_agent", "validation_agent")
            builder.add_conditional_edges(
                "validation_agent",
                self.next_step,
                {"retry": "inference_agent", "done": END},
            )
        self.graph = builder.compile()

    def after_preprocess(self, state: InterrogationState) -> str:
        """v1에서 RAG가 진술을 고르지 못한 질문은 검증 노드에서 마무리한다.

        Args:
            state: 전처리에서 확정한 승인 요청과 검색 결과.

        Returns:
            str: 검증으로 직행할지 생성 노드를 실행할지 결정하는 경로.
        """
        if (
            self.settings.validation_agent_version == "v1"
            and state.get("retrieval_no_match")
            and not state["request"].allowed_facts
        ):
            return "validate"
        return "generate"

    @staticmethod
    def next_step(state: InterrogationState) -> str:
        """검증이 요청한 경우에만 제한된 재생성을 수행한다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

        Returns:
            str: 재생성이 필요하면 retry, 종료하면 done.
        """
        if state.get("retry"):
            return "retry"
        return "done"

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
        """검증 에이전트에 후보 검사와 재생성 판단을 맡긴다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

        Returns:
            dict: 최종 응답 또는 재생성 여부와 거절 코드.
        """
        with trace_agent_time("validation_agent"):
            return await self.validator.validation_agent(state)

    # 기존 보고서 검사 호출 경로를 유지한다.
    _check_report_evidence = staticmethod(check_report_evidence)

    async def generate(
        self, request: CharacterReplyRequest, *, search_turn: SearchTurn | None = None
    ) -> CharacterReplyResponse:
        """그래프를 실행한다. 검색과 생성·검증에는 각각 제한 시간을 적용한다.

        Args:
            request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
            search_turn: 게임 규칙이 승인한 자유 질문 검색 정보 또는 None.

        Returns:
            CharacterReplyResponse: 검증을 통과하거나 승인 원문으로 복구한 최종 응답.
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
                if self.settings.validation_agent_version == "v1":
                    response = self.validator.output.failure(
                        request, 504, "pipeline_timeout"
                    )
                else:
                    response = neutral_response(request)
            trace["finish_reason"] = response.finish_reason
            trace["model_version"] = response.model_version
            return response
        except HTTPException as error:
            trace["http_status"] = error.status_code
            raise
        finally:
            finish_trace(trace, token, self.settings, started)
