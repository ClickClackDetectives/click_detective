"""정상 심문 대사를 생성하고 검증 실패 시 복구 정책을 적용한다."""

from app.dialogue.services.reply.dialogue_reply_validation import (
    validate_generation,
)
from app.dialogue.services.validation_agent.workflow.dialogue_validation_agent import (
    neutral_response,
)


class ReplyService:
    """대화 그래프를 실행하고 일반 심문의 검증·복구를 담당한다.

    Args:
        settings: 대화 검증과 실패 복구 정책을 담은 설정.
        graph: 검색·생성·검증을 수행하는 대화 그래프.
        search_free: 자유 질문의 진술 검색을 사용할 수 있는지 여부.

    Returns:
        ReplyService: 일반 심문과 내부 검사에 사용할 대화 서비스.
    """

    def __init__(self, settings, graph, *, search_free=False):
        """기동 시 준비한 대화 설정과 그래프를 보관한다.

        Args:
            settings: 대화 검증과 실패 복구를 설정하는 값.
            graph: 승인 문맥으로 대사를 생성하는 그래프.
            search_free: 자유 질문의 진술 검색을 사용할 수 있는지 여부.

        Returns:
            None: 반환값 없음.
        """
        self.settings = settings
        self.graph = graph
        self.search_free = search_free

    async def reply(self, request, search_turn=None):
        """쟁점 유무와 무관하게 대사를 준비하고 실행 예외는 설정에 따라 중립 응답으로 복구한다.

        Args:
            request: 승인 사실을 담은 대화 요청.
            search_turn: 첫 노드에서 확정할 자유 질문의 승인 계획 또는 None.

        Returns:
            CharacterReplyResponse: 검증된 대사 또는 중립 응답.
        """
        try:
            if search_turn is None:
                response = await self.graph.generate(request)
            else:
                response = await self.graph.generate(request, search_turn=search_turn)
                request = search_turn.request
            incomplete = response.finish_reason in {"partial", "neutral"}
            validate_generation(
                request,
                response,
                require_verbatim=response.finish_reason in {"fixed", "fallback"},
                require_all_facts=not incomplete,
            )
            return response
        except Exception:
            if search_turn is not None:
                if not search_turn.search_complete:
                    raise
                request = search_turn.request
            if not self.settings.fallback_on_error:
                raise
            return neutral_response(request)
