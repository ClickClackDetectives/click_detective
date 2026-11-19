"""후보 대사의 검증, 재생성 여부와 복구 응답을 결정한다."""

import asyncio

from pydantic import ValidationError

from ..diagnostics import trace_event
from ..local_model import ModelContextError
from ..reply_validation import FIXED_MODEL_VERSION, assemble_reply
from ..state import InterrogationState, OutputRejected
from .meaning_guards import has_question_actor_reversal
from .output import ReplyOutput
from .report_policy import VERIFICATION_FORMAT_CODES
from .verification import SemanticVerifier


class ValidationAgent:
    """후보 대사의 검사와 재생성·실패 처리를 조정한다.

    Args:
        settings: 모델 실행과 검색에 사용할 설정.
        model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

    Returns:
        ValidationAgent: 위 역할을 수행하도록 생성된 객체.
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
        self.output = ReplyOutput(settings, model)
        self.verifier = SemanticVerifier(settings, model)

    async def validation_agent(self, state: InterrogationState) -> dict:
        """에이전트 3: 규칙 검사 후 의미 검증을 수행하고 재생성 또는 최종 처리를 결정한다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

        Returns:
            dict: 최종 응답 또는 재생성 여부와 거절 코드.
        """
        request = state["request"]
        status = state.get("error_status")
        if status:
            code = "model_timeout" if status == 504 else "model_inference_failed"
            return {
                "response": self.output.failure(request, status, code),
                "retry": False,
            }
        code = "invalid_model_output"
        try:
            response = self.output.parse(request, state["raw_output"])
            trace_event(
                "generation_parsed",
                attempt=state.get("attempt"),
                format=self.settings.generation_output_format,
            )
            if any(
                has_question_actor_reversal(fact.text, response.reply)
                for fact in request.allowed_facts
            ):
                raise OutputRejected("actor_role_reversal")
            if not request.allowed_facts:
                if response.reply != assemble_reply(request) or response.used_fact_ids:
                    raise OutputRejected("unapproved_empty_reply")
                return {
                    "response": response.model_copy(
                        update={
                            "finish_reason": "fixed",
                            "model_version": FIXED_MODEL_VERSION,
                        }
                    ),
                    "retry": False,
                }
            code = "invalid_verification_output"
            async with asyncio.timeout(self.settings.timeout_seconds):
                response = await self.verifier.verify(request, response)
            return {"response": response, "retry": False}
        except OutputRejected as error:
            code = str(error)
            trace_event("candidate_rejected", code=code, attempt=state.get("attempt"))
        except ModelContextError:
            return {
                "response": self.output.failure(
                    request, 502, "verification_context_overflow"
                ),
                "retry": False,
            }
        except TimeoutError:
            return {
                "response": self.output.failure(request, 504, "verification_timeout"),
                "retry": False,
            }
        except RuntimeError:
            return {
                "response": self.output.failure(request, 502, "verification_failed"),
                "retry": False,
            }
        except ValidationError as error:
            code = (
                "invalid_generation_schema"
                if code == "invalid_model_output"
                else "invalid_verification_schema"
            )
            trace_event(
                "candidate_rejected",
                attempt=state.get("attempt"),
                code=code,
                error_types=sorted({item["type"] for item in error.errors()}),
            )
        except (ValueError, KeyError, TypeError):
            code = "invalid_generation_json" if code == "invalid_model_output" else code
            trace_event("candidate_rejected", attempt=state.get("attempt"), code=code)
        if code in VERIFICATION_FORMAT_CODES:
            return {"response": self.output.failure(request, 502, code), "retry": False}
        if state.get("attempt", 1) < self.settings.generation_attempts:
            return {"retry": True, "rejection_code": code}
        return {"response": self.output.failure(request, 502, code), "retry": False}
