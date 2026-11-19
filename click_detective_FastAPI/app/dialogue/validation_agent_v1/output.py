"""대사 출력 형식 검사와 승인 원문 복구를 담당한다."""

import json

from fastapi import HTTPException

from ..diagnostics import trace_event
from ..reply_validation import FIXED_MODEL_VERSION, assemble_reply, validate_generation
from ..schemas import CharacterReplyRequest, CharacterReplyResponse
from ..state import GeneratedReply, OutputRejected


class ReplyOutput:
    """모델 출력의 형식 검사와 승인 원문 복구를 담당한다.

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

    def failure(
        self, request: CharacterReplyRequest, status: int, code: str
    ) -> CharacterReplyResponse:
        """시도 상한 이후 고정 대체 응답이나 HTTP 오류로 처리한다.

        Args:
            request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
            status (int): 실패를 표현할 HTTP 상태 코드.
            code (str): 원문을 포함하지 않는 고정 오류 코드.

        Returns:
            CharacterReplyResponse: 승인 원문으로 구성한 복구 응답. 복구 비허용 시 HTTPException을 발생시킨다.
        """
        trace_event("failure", status=status, code=code)
        if not self.settings.fallback_on_error:
            if status == 504:
                message = "Generation timed out"
            else:
                message = "Generation service failed"
            raise HTTPException(status, message, headers={"X-Generation-Error": code})
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
