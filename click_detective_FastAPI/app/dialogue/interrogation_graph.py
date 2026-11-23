"""전처리 → 생성 → 검증의 연결과 전체 실행 시간을 관리한다."""

import asyncio
from time import perf_counter

from fastapi import HTTPException
from langgraph.graph import END, START, StateGraph

from ..config import Settings
from .diagnostics import finish_trace, start_trace, trace_agent_time
from .inference_agent.agent import InferenceAgent
from .local_model import ReplyModel
from .preprocess_agent.agent import PreprocessAgent
from .schemas import CharacterReplyRequest, CharacterReplyResponse
from .state import GeneratedReply as GeneratedReply
from .state import InterrogationState
from .state import OutputRejected as OutputRejected
from .validation_agent_v1.agent import ValidationAgent
from .validation_agent_v1.evidence_checks import check_report_evidence
from .validation_agent_v2.agent import ValidationAgentV2, neutral_response
from .validation_agent_v2.neutral import classify_neutral_question


class InterrogationGraph:
    """전처리·생성·검증의 실행 순서와 전체 시간 제한을 관리한다.

    Args:
        settings (Settings): 모델 실행과 검색에 사용할 설정.
        model (ReplyModel): 대사 생성과 의미 검증에 사용할 모델 실행 객체.

    Returns:
        InterrogationGraph: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, settings: Settings, model: ReplyModel) -> None:
        """한 모델을 생성·검증 호출에 공유한다. 검증자에게 생성자의 내부 추론은 전달하지 않는다.

        Args:
            settings (Settings): 모델 실행과 검색에 사용할 설정.
            model (ReplyModel): 대사 생성과 의미 검증에 사용할 모델 실행 객체.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.settings = settings
        self.model = model
        self.preprocessor = PreprocessAgent(settings)
        self.generator = InferenceAgent(settings, model)
        self.validator = (
            ValidationAgent(settings, model)
            if settings.validation_agent_version == "v1"
            else ValidationAgentV2(settings, model)
        )
        builder = StateGraph(InterrogationState)
        builder.add_node("preprocess_agent", self.preprocess_agent)
        builder.add_node("inference_agent", self.inference_agent)
        builder.add_node("validation_agent", self.validation_agent)
        builder.add_edge(START, "preprocess_agent")
        builder.add_edge("preprocess_agent", "inference_agent")
        builder.add_edge("inference_agent", "validation_agent")
        builder.add_conditional_edges(
            "validation_agent",
            self.next_step,
            {
                "retry": "inference_agent",
                "done": END,
            },
        )
        self.graph = builder.compile()

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

    async def preprocess_agent(self, state: InterrogationState) -> dict:
        """전처리 에이전트에 승인 사실 정리와 프롬프트 구성을 맡긴다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

        Returns:
            dict: 생성 프롬프트와 초기 생성 횟수.
        """
        with trace_agent_time("preprocess_agent"):
            return await self.preprocessor.preprocess_agent(state)

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

    async def generate(self, request: CharacterReplyRequest) -> CharacterReplyResponse:
        """생성·검증·재시도를 모두 포함한 전체 제한 시간 안에서 그래프를 실행한다.

        Args:
            request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.

        Returns:
            CharacterReplyResponse: 검증을 통과하거나 승인 원문으로 복구한 최종 응답.
        """
        started = perf_counter()
        trace, token = start_trace(request, self.settings)
        try:
            try:
                if (
                    self.settings.validation_agent_version != "v1"
                    and not request.allowed_facts
                    and classify_neutral_question(request.question) == "out_of_scope"
                ):
                    response = neutral_response(request)
                else:
                    async with asyncio.timeout(self.settings.timeout_seconds):
                        result = await self.graph.ainvoke({"request": request})
                    response = result["response"]
            except TimeoutError:
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
