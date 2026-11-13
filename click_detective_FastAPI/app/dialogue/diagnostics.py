"""비밀값·질문·모델 원문 없이 생성 원인을 추적하는 요청별 JSONL 진단 기록."""

from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
from time import perf_counter
from uuid import uuid4

PIPELINE_VERSION = "semantic-paraphrase-v7"

CURRENT_TRACE: ContextVar[dict | None] = ContextVar("generation_trace", default=None)
logger = logging.getLogger(__name__)


def trace_event(stage: str, **values) -> None:
    """현재 요청에 수치·고정 코드만 추가한다. 원문·토큰·개인정보를 전달하지 않는다."""
    trace = CURRENT_TRACE.get()
    if trace is not None:
        trace["events"].append({"stage": stage, **values})


def start_trace(request, settings) -> tuple[dict, object]:
    """실행 ID·시나리오 버전·비밀값을 제외한 유효 설정의 명시적 목록을 만든다."""
    trace = {
        "run_id": str(uuid4()), "request_id": str(request.request_id),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "scenario_version": request.scenario_version, "case_id": request.case_id,
        "pipeline_version": PIPELINE_VERSION, "events": [],
        "settings": {key: getattr(settings, key) for key in (
            "generation_mode", "generation_output_format", "local_model_version", "adapter_version", "rag_enabled", "rag_top_k",
            "max_input_tokens", "max_new_tokens", "history_limit", "generation_attempts",
            "verification_attempts", "verification_batch_size", "timeout_seconds", "fallback_on_error",
            "dialogue_temperature", "dialogue_top_p", "dialogue_repetition_penalty")},
    }
    return trace, CURRENT_TRACE.set(trace)


def finish_trace(trace, token, settings, started: float) -> None:
    """진단 저장 실패로 생성 결과를 바꾸지 않고 요청 문맥을 반드시 복원한다."""
    CURRENT_TRACE.reset(token)
    trace["completed_at"] = datetime.now(timezone.utc).isoformat()
    trace["elapsed_ms"] = round((perf_counter() - started) * 1000, 2)
    if not settings.diagnostics_enabled:
        return
    try:
        settings.diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
        with settings.diagnostics_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(trace, ensure_ascii=False) + "\n")
    except OSError:
        logger.warning("Generation diagnostics could not be written")
