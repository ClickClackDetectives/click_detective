"""HTTP와 게임 엔진·모델·원자적 저장을 조정한다. 게임 판정은 전부 Python이 담당한다."""

import logging

from fastapi import HTTPException

from ..dialogue.reply_validation import (
    FIXED_MODEL_VERSION,
    assemble_reply,
    validate_generation,
)
from ..dialogue.schemas import CharacterReplyRequest, CharacterReplyResponse
from ..dialogue.state import SearchTurn
from ..dialogue.validation_agent_v2.agent import neutral_response

logger = logging.getLogger(__name__)


class GameService:
    """수사 생성·조회·변경과 GPU 대사를 연결한다.

    Args:
        settings: 모델 실행과 검색에 사용할 설정.
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
        repository: 수사 상태와 요청 예약을 저장하는 객체.
        engine: 게임 진행과 행동의 조건을 판정하는 객체.
        planner: 현재 공개할 사실을 선택하는 객체.
        presenter: 내부 상태를 화면용 정보로 변환하는 객체.
        graph: 검색·생성·검증을 수행하는 그래프.
        search_free: 그래프에서 자유 질문의 진술을 검색할 수 있는지 여부.

    Returns:
        GameService: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(
        self,
        settings,
        catalog,
        repository,
        engine,
        planner,
        presenter,
        graph,
        *,
        search_free=False,
    ):
        """공용 객체를 연결한다. 모델은 서버 시작 시 한 번만 준비한다.

        Args:
            settings: 모델 실행과 검색에 사용할 설정.
            catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
            repository: 수사 상태와 요청 예약을 저장하는 객체.
            engine: 게임 진행과 행동의 조건을 판정하는 객체.
            planner: 현재 공개할 사실을 선택하는 객체.
            presenter: 내부 상태를 화면용 정보로 변환하는 객체.
            graph: 검색·생성·검증을 수행하는 그래프.
            search_free: 그래프에서 자유 질문의 진술을 검색할 수 있는지 여부.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.settings = settings
        self.catalog = catalog
        self.repository = repository
        # 이전 연동 코드가 사용하는 속성 이름도 유지한다.
        self.c = catalog
        self.repo = repository
        self.engine = engine
        self.planner = planner
        self.presenter = presenter
        self.graph = graph
        self.search_free = search_free

    def read(self, game_id, token):
        """소유권과 사건 버전을 검사해 저장 상태를 복원한다.

        Args:
            game_id: 조회하거나 변경할 수사의 식별자.
            token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.

        Returns:
            dict: 소유권과 사건 버전을 확인한 수사 상태.
        """
        state = self.repository.get(game_id, token)
        if state["scenarioVersion"] != self.catalog.version:
            raise HTTPException(409, "scenario_version_conflict")
        return state

    def create(self, command):
        """실행 가능한 사건·버전을 확인하고 생성 중복을 처리한다.

        Args:
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

        Returns:
            dict: 수사 ID, 접근 토큰과 공개 초기 상태 또는 저장된 동일 요청 결과.
        """
        self.catalog.require_case(command.case_id)
        if command.scenario_version != self.catalog.version:
            raise HTTPException(409, "scenario_version_conflict")
        return self.repository.create(
            command, self.engine.initial, self.presenter.state
        )

    def dialogue_request(self, state, command, plan):
        """저장 상태와 승인 계획에서 모델 DTO를 만든다. 외부 임의 승인 사실을 받지 않는다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
            plan: 게임 규칙이 승인한 사실과 기록 예정 정보를 담은 계획.

        Returns:
            CharacterReplyRequest: 승인 사실, 필수 ID, 인물과 최근 대화를 담은 요청.
        """
        history = []
        if self.settings.history_limit:
            for message in state["messages"]:
                if message["suspectId"] == plan.suspect_id:
                    history.append({"role": message["role"], "text": message["text"]})
            history = history[-self.settings.history_limit :]
        person = self.catalog.people[plan.suspect_id]
        speech_style = person.get("speech_style")
        if not isinstance(speech_style, str) or not speech_style.strip():
            speech_style = "존댓말. 승인 원문의 말투와 관찰 한계를 유지하세요."
        return CharacterReplyRequest(
            request_id=command.request_id,
            game_id=state["id"],
            case_id=self.catalog.case_id,
            scenario_version=self.catalog.version,
            state_revision=state["revision"],
            turn_index=state["questions"] + 1,
            suspect_id=plan.suspect_id,
            phase=state["phase"],
            question=plan.question,
            topic_id=plan.topic,
            persona={
                "name": person["name"],
                "role": person["role"],
                "speech_style": speech_style,
            },
            allowed_facts=plan.facts,
            required_fact_ids=[fact["id"] for fact in plan.facts],
            history=history,
        )

    async def reply(self, request, search_turn=None):
        """쟁점 유무와 무관하게 대사를 준비하고 모델 실패는 승인 원문으로 복구한다.

        Args:
            request: 승인 사실을 담은 대화 요청.
            search_turn: 첫 노드에서 확정할 자유 질문의 승인 계획 또는 None.

        Returns:
            CharacterReplyResponse: 생성·검증을 통과했거나 승인 원문으로 복구한 응답.
        """
        try:
            if search_turn is None:
                response = await self.graph.generate(request)
            else:
                response = await self.graph.generate(request, search_turn=search_turn)
                request = search_turn.request
            incomplete = (
                self.settings.validation_agent_version != "v1"
                and response.finish_reason in {"partial", "neutral"}
            )
            validate_generation(
                request,
                response,
                require_verbatim=response.finish_reason in {"fixed", "fallback"},
                require_all_facts=not incomplete,
            )
            return response
        except Exception as error:
            if search_turn is not None:
                if not search_turn.search_complete:
                    raise
                request = search_turn.request
            if not self.settings.fallback_on_error:
                raise
            if self.settings.validation_agent_version != "v1":
                return neutral_response(request)
            logger.warning(
                "Dialogue recovered with approved facts: error_type=%s status=%s",
                type(error).__name__,
                getattr(error, "status_code", None),
            )
            response = CharacterReplyResponse(
                request_id=request.request_id,
                suspect_id=request.suspect_id,
                state_revision=request.state_revision,
                reply=assemble_reply(request),
                used_fact_ids=[fact.id for fact in request.allowed_facts],
                model_version=FIXED_MODEL_VERSION,
                finish_reason="fallback",
            )
            validate_generation(request, response)
            return response

    async def change(self, game_id, token, command, action):
        """짧은 예약→규칙·생성→짧은 확정. 중간 실패는 질문·쟁점·revision을 소비하지 않는다.

        Args:
            game_id: 조회하거나 변경할 수사의 식별자.
            token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
            action: 실행할 수사 행동 이름. 예: interrogate, examine.

        Returns:
            dict: 확정한 행동 결과와 최신 공개 상태 또는 저장된 동일 요청 응답.
        """
        reservation = self.repository.reserve(
            game_id, token, command, action, self.settings.timeout_seconds * 2 + 30
        )
        if "cached" in reservation:
            return reservation["cached"]
        try:
            state = reservation["state"]
            self.engine.require_active(state)
            if action == "examine":
                result = self.engine.examine(state, command)
            elif action == "infer":
                result = self.engine.infer(state, command)
            elif action == "advance":
                result = self.engine.advance(state, command)
            elif action == "notes":
                state["notes"] = command.text
                result = {"saved": True}
            elif action == "accuse":
                result = self.engine.accuse(state, command)
            elif action == "interrogate":
                search_free = self.settings.rag_enabled and self.search_free
                plan = self.planner.prepare(state, command, search_free=search_free)
                request = self.dialogue_request(state, command, plan)
                turn = None
                if search_free and not plan.topic and not plan.new_findings:
                    turn = SearchTurn(plan, request, tuple(state["revealed"]))
                response = await self.reply(request, turn)
                if turn is not None:
                    plan = turn.plan
                result = self.engine.record_plan(state, plan, response)
            else:
                raise HTTPException(404, "행동을 찾을 수 없습니다.")
            return self.repository.commit(
                game_id, command, reservation, state, result, self.presenter.state
            )
        finally:
            self.repository.abort(command, reservation)
