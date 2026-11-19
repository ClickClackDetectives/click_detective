"""비밀값·질문·모델 원문 없이 생성 원인을 추적하는 요청별 JSONL 진단 기록."""

import json
import logging
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

PIPELINE_VERSION = "semantic-paraphrase-v7"

CURRENT_TRACE: ContextVar[dict | None] = ContextVar("generation_trace", default=None)
logger = logging.getLogger(__name__)


def trace_event(stage: str, **values) -> None:
    """현재 요청에 수치·고정 코드만 추가한다. 원문·토큰·개인정보를 전달하지 않는다.

    Args:
        stage (str): 진단 이벤트의 단계 이름.
        values: 원문이나 비밀값을 제외한 진단 수치와 고정 코드.

    Returns:
        None: 반환값 없음.
    """
    trace = CURRENT_TRACE.get()
    if trace is not None:
        trace["events"].append({"stage": stage, **values})


@contextmanager
def trace_agent_time(agent: str):
    """에이전트의 한 번의 호출에 걸린 시간을 기록한다.

    Args:
        agent: 그래프에 등록된 에이전트 이름.

    Returns:
        Iterator: 예외나 취소가 발생해도 종료 시점까지 측정하는 문맥.
    """
    started = perf_counter()
    try:
        yield
    finally:
        trace_event(
            "agent_timing",
            agent=agent,
            elapsed_ms=round((perf_counter() - started) * 1000, 2),
        )


def start_trace(request, settings) -> tuple[dict, object]:
    """실행 ID·시나리오 버전·비밀값을 제외한 유효 설정의 명시적 목록을 만든다.

    Args:
        request: 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
        settings: 모델 실행과 검색에 사용할 설정.

    Returns:
        tuple[dict, object]: 새 진단 기록과 이전 요청 문맥을 복원할 토큰.
    """
    trace = {
        "run_id": str(uuid4()),
        "request_id": str(request.request_id),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "scenario_version": request.scenario_version,
        "case_id": request.case_id,
        "pipeline_version": PIPELINE_VERSION,
        "events": [],
        "settings": {
            key: getattr(settings, key)
            for key in (
                "generation_mode",
                "validation_agent_version",
                "validation_similarity_threshold",
                "validation_similarity_backend",
                "generation_output_format",
                "local_model_version",
                "adapter_version",
                "rag_enabled",
                "rag_top_k",
                "max_input_tokens",
                "max_new_tokens",
                "history_limit",
                "generation_attempts",
                "verification_attempts",
                "verification_batch_size",
                "timeout_seconds",
                "fallback_on_error",
                "dialogue_temperature",
                "dialogue_top_p",
                "dialogue_repetition_penalty",
            )
        },
    }
    return trace, CURRENT_TRACE.set(trace)


def finish_trace(trace, token, settings, started: float) -> None:
    """진단 저장 실패로 생성 결과를 바꾸지 않고 요청 문맥을 반드시 복원한다.

    Args:
        trace: 현재 요청의 진단 정보와 이벤트 목록.
        token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.
        settings: 모델 실행과 검색에 사용할 설정.
        started (float): 실행 시작 시점의 성능 측정 타이머 값.

    Returns:
        None: 반환값 없음.
    """
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
