"""모델 대사의 형식과 사실 식별자를 검사한다."""

import json

from app.dialogue.dto.dialogue_graph_state import GeneratedReply
from app.dialogue.dto.dialogue_reply_dto import (
    CharacterReplyRequest,
    CharacterReplyResponse,
)
from app.dialogue.services.diagnostics.dialogue_diagnostics import trace_event
from app.dialogue.services.validation_agent.output.dialogue_output_rejected import (
    OutputRejected,
)


class ReplyOutput:
    """모델 출력의 형식과 승인 사실 ID를 검사한다.

    Args:
        settings: 모델 실행과 검색에 사용할 설정.
        model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

    Returns:
        ReplyOutput: 위 역할을 수행하도록 생성된 객체.
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

    def parse(self, request: CharacterReplyRequest, raw: str) -> CharacterReplyResponse:
        """JSON·길이·선택적 ID를 규칙으로 검사한다. 의미 검증은 별도 호출로 수행한다.

        Args:
            request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
            raw (str): 모델이 반환한 가공 전 출력 문자열.

        Returns:
            CharacterReplyResponse: 출력 형식과 사실 ID를 검사한 후보 응답.
        """
        stripped = raw.lstrip()
        if not stripped:
            shape = "empty"
        elif stripped.startswith("```"):
            shape = "markdown"
        elif stripped.startswith("{"):
            shape = "object_like"
        elif stripped.startswith("["):
            shape = "array_like"
        else:
            shape = "plain_text"
        trace_event(
            "generation_format",
            expected=self.settings.generation_output_format,
            observed_shape=shape,
            output_characters=len(raw),
        )
        if self.settings.generation_output_format == "text":
            if raw.lstrip().startswith(("{", "[", "```")):
                raise OutputRejected("unexpected_generation_format")
            parsed = GeneratedReply(reply=raw.strip())
        else:
            try:
                data = json.loads(raw)
            except (ValueError, TypeError):
                raise OutputRejected("invalid_generation_json") from None
            parsed = GeneratedReply.model_validate(data)
        response = CharacterReplyResponse(
            request_id=request.request_id,
            suspect_id=request.suspect_id,
            state_revision=request.state_revision,
            reply=parsed.reply,
            used_fact_ids=parsed.used_fact_ids,
            model_version=self.model.model_version,
            finish_reason="stop",
        )
        allowed_ids = set()
        for fact in request.allowed_facts:
            allowed_ids.add(fact.id)
        if len(parsed.used_fact_ids) != len(set(parsed.used_fact_ids)) or not set(
            parsed.used_fact_ids
        ).issubset(allowed_ids):
            raise OutputRejected("invalid_fact_ids")
        return response
