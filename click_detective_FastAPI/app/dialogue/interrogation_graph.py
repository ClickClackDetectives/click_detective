"""전처리 → 자유 대사 생성 → 의미 검증. 실패 시 제한된 재생성 후 fallback한다.

공개 사실은 FastAPI 승인 계획에서 결정한다. 생성·검증은 같은 로컬 모델의 별도 호출을 사용하며
의미 검증은 확률적 판단이다. 검증 통과가 사실성의 수학적 보장을 뜻하지는 않는다.
"""

import asyncio
import json
from typing import TypedDict
from time import perf_counter

from .diagnostics import start_trace, finish_trace, trace_event
from .verification_units import build_verification_units
from .semantic_verification import SemanticReport, candidate_sentences
from .meaning_guards import has_question_actor_reversal
from .critical_facts import critical_claim_error, critical_evidence_error

from fastapi import HTTPException
from langgraph.graph import END, START, StateGraph
from pydantic import Field, ValidationError

from ..config import Settings
from .rag.retriever import RetrievalContext, retrieve_approved_facts
from .local_model import ModelContextError, ReplyModel
from .prompting import build_messages, build_verification_messages
from .reply_validation import FIXED_MODEL_VERSION, assemble_reply, validate_generation
from .schemas import CharacterReplyRequest, CharacterReplyResponse, DTO, Identifier, ReplyText


class GeneratedReply(DTO):
    """모델이 직접 작성한 대사. 선택적 ID 자기 신고는 허용 범위만 검사하며 별도 검증한다."""

    reply: ReplyText
    used_fact_ids: list[Identifier] = Field(default_factory=list, max_length=10)


class OutputRejected(ValueError):
    """고정 오류 코드와 안전한 하위 사유. 모델 원문·프롬프트는 담지 않는다."""

    def __init__(self, code: str, detail: str = "") -> None:
        """HTTP 코드는 유지하고 내부 형식 실패 원인을 별도로 추적한다."""
        super().__init__(code)
        self.detail = detail



class InterrogationState(TypedDict, total=False):
    """요청별 지역 상태. 원본 생성·검증 내용은 DB나 GameState에 저장하지 않는다."""

    request: CharacterReplyRequest
    messages: list[dict[str, str]]
    retrieval: RetrievalContext
    raw_output: str
    attempt: int
    error_status: int | None
    retry: bool
    rejection_code: str
    response: CharacterReplyResponse


class InterrogationGraph:
    """세 노드를 연결한다. 검증 실패만 생성 노드로 되돌아가며 횟수와 전체 시간을 제한한다."""

    def __init__(self, settings: Settings, model: ReplyModel) -> None:
        """한 모델을 생성·검증 호출에 공유한다. 검증자에게 생성자의 내부 추론은 전달하지 않는다."""
        self.settings = settings
        self.model = model
        builder = StateGraph(InterrogationState)
        builder.add_node("preprocess_agent", self.preprocess_agent)
        builder.add_node("inference_agent", self.inference_agent)
        builder.add_node("validation_agent", self.validation_agent)
        builder.add_edge(START, "preprocess_agent")
        builder.add_edge("preprocess_agent", "inference_agent")
        builder.add_edge("inference_agent", "validation_agent")
        builder.add_conditional_edges("validation_agent", self.next_step, {
            "retry": "inference_agent", "done": END,
        })
        self.graph = builder.compile()

    @staticmethod
    def next_step(state: InterrogationState) -> str:
        """검증이 요청한 경우에만 제한된 재생성을 수행한다."""
        return "retry" if state.get("retry") else "done"

    async def preprocess_agent(self, state: InterrogationState) -> dict:
        """에이전트 1: 승인 사실 안에서 검색하고 필수 사실을 보존하여 문맥을 만든다."""
        request = state["request"]
        if len(build_verification_units(request)) > 256:
            raise HTTPException(422, "Approved context contains too many verification sentences")
        retrieval = retrieve_approved_facts(request, self.settings.rag_top_k, self.settings.rag_enabled)
        trace_event("retrieval", approved_count=len(request.allowed_facts), selected_count=len(retrieval.selected_facts),
                    required_count=len(request.required_fact_ids), unit_count=len(build_verification_units(request)))
        return {"messages": build_messages(request, self.settings, retrieval), "retrieval": retrieval, "attempt": 0}

    async def inference_agent(self, state: InterrogationState) -> dict:
        """에이전트 2: 사실의 의미를 유지하며 표현을 샘플링한다. 원문 복사를 요구하지 않는다."""
        if not state["request"].allowed_facts:
            trace_event("empty_approval", policy="deterministic_neutral", model_calls=0)
            return {"attempt": 0, "raw_output": (json.dumps({"reply": assemble_reply(state["request"])})
                        if self.settings.generation_output_format == "json" else assemble_reply(state["request"])),
                    "error_status": None, "retry": False}
        messages = list(state["messages"])
        if state.get("rejection_code"):
            output_rule = ('캐릭터 대사 원문만 출력하고 JSON·해설은 쓰지 마세요.'
                           if self.settings.generation_output_format == "text" else
                           'reply를 담은 JSON 객체 하나만 출력하세요.')
            messages.append({"role": "user", "content": (
                f"이전 시도 검증 코드: {state['rejection_code']}. "
                "required_sentences는 복사할 정답이 아니라 보존할 의미 목록입니다. "
                "행동·시각·부정·관찰 한계는 유지하되 문장 구성과 표현은 자연스럽게 바꾸세요. "
                "특히 시각 누락 오류이면 해당 시각과 연결된 행동을 함께 명시하세요. " + output_rule
            )})
        result = {"attempt": state.get("attempt", 0) + 1, "error_status": None, "retry": False}
        try:
            async with asyncio.timeout(self.settings.timeout_seconds):
                started = perf_counter()
                raw = await self.model.generate(messages, purpose="dialogue")
                trace_event("generation", attempt=result["attempt"], elapsed_ms=round((perf_counter()-started)*1000, 2))
            return result | {"raw_output": raw}
        except ModelContextError:
            raise HTTPException(422, "Approved context exceeds local token budget") from None
        except TimeoutError:
            return result | {"error_status": 504}
        except (RuntimeError, ValueError):
            return result | {"error_status": 502}

    def _validate_model_output(self, request: CharacterReplyRequest, raw: str) -> CharacterReplyResponse:
        """JSON·길이·선택적 ID를 규칙으로 검사한다. 의미 검증은 별도 호출로 수행한다."""
        stripped = raw.lstrip()
        shape = ("empty" if not stripped else "markdown" if stripped.startswith("```")
                 else "object_like" if stripped.startswith("{") else "array_like" if stripped.startswith("[")
                 else "plain_text")
        trace_event("generation_format", expected=self.settings.generation_output_format,
                    observed_shape=shape, output_characters=len(raw))
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
            request_id=request.request_id, suspect_id=request.suspect_id,
            state_revision=request.state_revision, reply=parsed.reply,
            used_fact_ids=parsed.used_fact_ids, model_version=self.model.model_version,
            finish_reason="stop",
        )
        allowed_ids = {fact.id for fact in request.allowed_facts}
        if len(parsed.used_fact_ids) != len(set(parsed.used_fact_ids)) or not set(parsed.used_fact_ids).issubset(allowed_ids):
            raise OutputRejected("invalid_fact_ids")
        return response

    @staticmethod
    def _check_report_evidence(
        report: SemanticReport, request: CharacterReplyRequest, reply: str, units=None,
    ) -> set[str]:
        """판정 자체에 앞서 항목의 완전성과 실제 원문 인용을 검사한다."""
        all_units = build_verification_units(request)
        units = all_units if units is None else units
        expected = {int(unit.id.removeprefix("unit-")) for unit in units}
        checked = [index for index, _, _ in report.checks]
        if len(checked) != len(set(checked)) or set(checked) != expected:
            reason = "duplicate_unit_indexes" if len(checked) != len(set(checked)) else "unit_index_set_mismatch"
            trace_event("verification_unit_issue", reason=reason, expected_count=len(expected), actual_count=len(checked))
            raise OutputRejected("verification_fact_ids_mismatch", reason)
        sentences = candidate_sentences(reply)
        valid_ids = {part.id for part in sentences}
        supported_ids = set()
        for index, supported, evidence in report.checks:
            reason = ""
            if len(evidence) != len(set(evidence)):
                reason = "duplicate_evidence_ids"
            elif not set(evidence).issubset(valid_ids):
                reason = "out_of_range_evidence_id"
            elif supported and not evidence:
                reason = "missing_positive_evidence"
            elif not supported and evidence:
                reason = "unexpected_negative_evidence"
            if reason:
                trace_event("verification_evidence_issue", reason=reason, unit_index=index,
                            candidate_sentence_count=len(sentences))
                raise OutputRejected("verification_evidence_mismatch", reason)
            if supported:
                evidence_text = " ".join(sentences[part_id].text for part_id in sorted(evidence))
                guard = critical_evidence_error(all_units[index].text, evidence_text)
                if guard:
                    raise OutputRejected(guard)
                supported_ids.add(index)
        return {fact.id for fact in request.allowed_facts
                if any(unit.fact_id == fact.id for unit in units)
                and all(int(unit.id.removeprefix("unit-")) in supported_ids
                        for unit in units if unit.fact_id == fact.id)}

    async def _request_verification_report(
        self, request: CharacterReplyRequest, reply: str,
    ) -> tuple[SemanticReport, set[str]]:
        """형식·근거가 잘못된 검증 응답만 재요청한다. 의미상 거절 판정을 뒤집기 위한 재시도는 하지 않는다.

        모델의 비JSON 텍스트를 삭제·수선하거나 누락 판정을 기본값으로 채우지 않는다.
        같은 후보 대사를 유지하며 새 JSON도 파싱·스키마·항목·인용 검사를 전부 통과해야 한다.
        """
        units = build_verification_units(request)
        reports = []
        # 출력이 길어져 JSON이 잘리지 않도록 작은 묶음으로 검사한다. 전체 승인 계획은 매번 유지한다.
        batches = [units[index:index + self.settings.verification_batch_size]
                   for index in range(0, len(units), self.settings.verification_batch_size)] or [[]]
        for batch_index, batch in enumerate(batches):
            messages = build_verification_messages(request, self.settings, reply)
            context = json.loads(messages[1]["content"])
            context["verification_units"] = [
                {"index": int(unit.id.removeprefix("unit-")), "fact_id": unit.fact_id}
                for unit in batch
            ]
            messages[1]["content"] = json.dumps(context, ensure_ascii=False, separators=(",", ":"))
            expected_ids = [int(unit.id.removeprefix("unit-")) for unit in batch]
            messages.append({"role": "user", "content": (
                f"이번 checks의 index는 {json.dumps(expected_ids)}를 빠짐없이 각각 한 번씩 반환하세요. "
                f"checks는 정확히 {len(expected_ids)}개입니다. fact_id 개수가 아니라 검증 문장 개수입니다. "
                "각 문장에 대해 true이면 실제 후보 문장 번호, false이면 빈 배열 []을 사용하세요."
            )})
            last_code = "invalid_verification_output"
            last_detail = ""
            for attempt in range(self.settings.verification_attempts):
                current_messages = list(messages)
                if attempt:
                    current_messages.append({"role": "user", "content": (
                        f"검증 형식 오류: {last_code}/{last_detail}. 필요한 checks index 목록: {json.dumps(expected_ids)}. "
                        f"선택 가능한 후보 문장 번호: {[part.id for part in candidate_sentences(reply)]}. "
                        "같은 후보를 다시 검사하고 JSON 객체 하나만 반환하세요. "
                        "checks=[index, true, [후보문장번호]] 또는 [index, false, []]입니다. "
                        "false 판정에는 근거 번호를 절대로 넣지 마세요. 모든 index를 검사하세요."
                    )})
                started = perf_counter()
                raw = await self.model.generate(current_messages, purpose="verification")
                trace_event("verification", batch=batch_index + 1, attempt=attempt + 1,
                            elapsed_ms=round((perf_counter()-started)*1000, 2))
                try:
                    data = json.loads(raw)
                except (ValueError, TypeError):
                    last_code = "invalid_verification_json"
                    last_detail = ""
                else:
                    try:
                        report = SemanticReport.model_validate(data)
                        self._check_report_evidence(report, request, reply, batch)
                    except ValidationError:
                        last_code = "invalid_verification_schema"
                        last_detail = ""
                    except OutputRejected as error:
                        if str(error) != "verification_evidence_mismatch" and str(error) != "verification_fact_ids_mismatch":
                            raise
                        last_code = str(error)
                        last_detail = error.detail
                    else:
                        # 의미상 거절은 같은 후보로 재검증하지 않고 바로 생성 재시도 정책에 넘긴다.
                        for rejected, code in (
                            (report.uncertain, "semantic_uncertain"),
                            (report.has_contradiction, "contradictory_reply"),
                            (report.has_unsupported_claims, "unsupported_claims"),
                            (not report.history_consistent, "history_conflict"),
                            (not report.persona_consistent, "persona_mismatch"),
                        ):
                            if rejected:
                                raise OutputRejected(code)
                        reports.append(report)
                        break
                trace_event("verification_rejected", batch=batch_index + 1, code=last_code, detail=last_detail)
            else:
                raise OutputRejected(last_code)
        # 모든 묶음의 부정 판정을 보존한다. 다른 묶음의 긍정 판정으로 덮어쓰지 않는다.
        combined = SemanticReport(
            checks=[check for report in reports for check in report.checks],
            has_contradiction=any(report.has_contradiction for report in reports),
            has_unsupported_claims=any(report.has_unsupported_claims for report in reports),
            history_consistent=all(report.history_consistent for report in reports),
            persona_consistent=all(report.persona_consistent for report in reports),
            uncertain=any(report.uncertain for report in reports),
        )
        return combined, self._check_report_evidence(combined, request, reply)

    async def _verify_semantics(self, request: CharacterReplyRequest, response: CharacterReplyResponse) -> CharacterReplyResponse:
        """별도 모델 호출의 의미 판정을 확인한다. 형식 재시도 후에도 불확실하면 거절한다."""
        guard = critical_claim_error(request, response.reply)
        if guard:
            trace_event("critical_claim_rejected", code=guard)
            raise OutputRejected(guard)
        report, supported_ids = await self._request_verification_report(request, response.reply)
        if report.uncertain:
            raise OutputRejected("semantic_uncertain")
        if report.has_contradiction:
            raise OutputRejected("contradictory_reply")
        if report.has_unsupported_claims:
            raise OutputRejected("unsupported_claims")
        if not report.history_consistent:
            raise OutputRejected("history_conflict")
        if not report.persona_consistent:
            raise OutputRejected("persona_mismatch")
        if not set(request.required_fact_ids).issubset(supported_ids):
            raise OutputRejected("missing_fact_meaning")
        if response.used_fact_ids and supported_ids != set(response.used_fact_ids):
            raise OutputRejected("fact_coverage_mismatch")
        # 최종 사실 ID는 생성자의 자기 신고가 아닌 별도 검증 결과에서 만든다.
        verified_response = response.model_copy(update={
            "used_fact_ids": [fact.id for fact in request.allowed_facts if fact.id in supported_ids]
        })
        validate_generation(request, verified_response, require_verbatim=False)
        return verified_response

    def _failure(self, request: CharacterReplyRequest, status: int, code: str) -> CharacterReplyResponse:
        """시도 상한 이후 고정 대체 응답이나 HTTP 오류로 처리한다."""
        trace_event("failure", status=status, code=code)
        if not self.settings.fallback_on_error:
            message = "Generation timed out" if status == 504 else "Generation service failed"
            raise HTTPException(status, message, headers={"X-Generation-Error": code})
        response = CharacterReplyResponse(
            request_id=request.request_id, suspect_id=request.suspect_id,
            state_revision=request.state_revision, reply=assemble_reply(request),
            used_fact_ids=[fact.id for fact in request.allowed_facts],
            model_version=FIXED_MODEL_VERSION, finish_reason="fallback",
        )
        validate_generation(request, response)
        return response

    async def validation_agent(self, state: InterrogationState) -> dict:
        """에이전트 3: 규칙 검사 후 의미 검증을 수행하고 재생성 또는 최종 처리를 결정한다."""
        request = state["request"]
        status = state.get("error_status")
        if status:
            code = "model_timeout" if status == 504 else "model_inference_failed"
            return {"response": self._failure(request, status, code), "retry": False}
        code = "invalid_model_output"
        try:
            response = self._validate_model_output(request, state["raw_output"])
            trace_event("generation_parsed", attempt=state.get("attempt"), format=self.settings.generation_output_format)
            if any(has_question_actor_reversal(fact.text, response.reply) for fact in request.allowed_facts):
                raise OutputRejected("actor_role_reversal")
            if not request.allowed_facts:
                if response.reply != assemble_reply(request) or response.used_fact_ids:
                    raise OutputRejected("unapproved_empty_reply")
                return {"response": response.model_copy(update={"finish_reason": "fixed",
                        "model_version": FIXED_MODEL_VERSION}), "retry": False}
            code = "invalid_verification_output"
            async with asyncio.timeout(self.settings.timeout_seconds):
                response = await self._verify_semantics(request, response)
            return {"response": response, "retry": False}
        except OutputRejected as error:
            code = str(error)
            trace_event("candidate_rejected", code=code, attempt=state.get("attempt"))
        except ModelContextError:
            return {"response": self._failure(request, 502, "verification_context_overflow"), "retry": False}
        except TimeoutError:
            return {"response": self._failure(request, 504, "verification_timeout"), "retry": False}
        except RuntimeError:
            return {"response": self._failure(request, 502, "verification_failed"), "retry": False}
        except ValidationError as error:
            code = "invalid_generation_schema" if code == "invalid_model_output" else "invalid_verification_schema"
            trace_event("candidate_rejected", attempt=state.get("attempt"), code=code,
                        error_types=sorted({item["type"] for item in error.errors()}))
        except (ValueError, KeyError, TypeError):
            code = "invalid_generation_json" if code == "invalid_model_output" else code
            trace_event("candidate_rejected", attempt=state.get("attempt"), code=code)
        verification_format_codes = {
            "invalid_verification_json", "invalid_verification_schema",
            "verification_fact_ids_mismatch", "verification_evidence_mismatch",
        }
        if code in verification_format_codes:
            return {"response": self._failure(request, 502, code), "retry": False}
        if state.get("attempt", 1) < self.settings.generation_attempts:
            return {"retry": True, "rejection_code": code}
        return {"response": self._failure(request, 502, code), "retry": False}

    async def generate(self, request: CharacterReplyRequest) -> CharacterReplyResponse:
        """생성·검증·재시도를 모두 포함한 전체 제한 시간 안에서 그래프를 실행한다."""
        started = perf_counter()
        trace, token = start_trace(request, self.settings)
        try:
            try:
                async with asyncio.timeout(self.settings.timeout_seconds):
                    result = await self.graph.ainvoke({"request": request})
                response = result["response"]
            except TimeoutError:
                response = self._failure(request, 504, "pipeline_timeout")
            trace["finish_reason"] = response.finish_reason
            trace["model_version"] = response.model_version
            return response
        except HTTPException as error:
            trace["http_status"] = error.status_code
            raise
        finally:
            finish_trace(trace, token, self.settings, started)
