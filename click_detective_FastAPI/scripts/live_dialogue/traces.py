"""서버의 대화 생성 진단을 실서버 검사 보고서에 연결한다."""

import json


def summarize_agent_timings(events):
    """에이전트별 호출 시간과 합계를 밀리초 단위로 정리한다.

    Args:
        events: 해당 심문 요청의 서버 진단 이벤트 목록.

    Returns:
        dict: 측정된 에이전트별 호출 시간 목록과 합계.
    """
    durations = {}
    for event in events:
        if event.get("stage") != "agent_timing":
            continue
        agent = event.get("agent")
        elapsed_ms = event.get("elapsed_ms")
        if isinstance(agent, str) and isinstance(elapsed_ms, (int, float)):
            durations.setdefault(agent, []).append(elapsed_ms)
    return {
        agent: {"calls_ms": calls, "total_ms": round(sum(calls), 2)}
        for agent, calls in durations.items()
    }


def attach_traces(report, trace_path, required=False):
    """같은 서버의 진단 JSONL을 선택적으로 읽어 요청별 3단계 호출 증거를 연결한다.

    Args:
        report: 검사 결과와 실행 기록을 담은 보고서.
        trace_path: 같은 서버가 기록한 진단 JSONL 파일 경로.
        required: 실행 진단 확인을 검사 통과의 필수 조건으로 적용할지 여부.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    ids = {case["request_id"] for case in report["cases"] if case["request_id"]}
    traces = {}
    error = None
    try:
        with trace_path.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    trace = json.loads(line)
                    if trace.get("request_id") in ids:
                        traces[trace["request_id"]] = trace
                except (ValueError, AttributeError):
                    continue
    except OSError as exception:
        error = str(exception)
    for case in report["cases"]:
        trace = traces.get(case["request_id"])
        events = (trace or {}).get("events", [])
        stages = {event.get("stage") for event in events}
        case["agent_timings"] = summarize_agent_timings(events)
        settings = (trace or {}).get("settings") or {}
        expected_version = report.get("expected_validation_agent_version")
        neutral_category = case.get("expected_neutral_category")
        skips_model = neutral_category == "out_of_scope"
        if neutral_category:
            category_ok = any(
                event.get("stage") == "validation_outcome"
                and event.get("neutral_category") == neutral_category
                for event in events
            )
            if skips_model:
                category_ok = (
                    category_ok
                    and not {
                        "agent_timing",
                        "generation",
                        "verification",
                    }
                    & stages
                )
            case["checks"]["expected_neutral_category"] = category_ok
            if (required or expected_version) and not category_ok:
                case["passed"] = False
                case["error"] = (
                    case.get("error", "")
                    + " 중립 분류 또는 실행 진단이 일치하지 않습니다."
                ).strip()
        if expected_version:
            observed = settings.get("validation_agent_version")
            case["validation_agent_version"] = observed
            version_ok = observed == expected_version
            timings_ok = (
                skips_model
                or {
                    "preprocess_agent",
                    "inference_agent",
                    "validation_agent",
                }
                <= case["agent_timings"].keys()
            )
            case["checks"]["validation_agent_version"] = version_ok
            if not skips_model:
                case["checks"]["agent_timings_present"] = timings_ok
            case["passed"] = case["passed"] and version_ok and timings_ok
            if not version_ok or not timings_ok:
                case["error"] = (
                    case.get("error", "")
                    + " 일치하는 검증 버전 또는 에이전트 시간 기록이 부족합니다."
                ).strip()
        confirmed = (
            bool(trace)
            and (trace.get("settings") or {}).get("generation_mode") == "local"
            and bool({"preprocess", "retrieval"} & stages)
            and {"generation", "verification"} <= stages
        )
        resources = [
            event for event in events if event.get("stage") == "model_resources"
        ]
        quantized = bool(resources) and all(
            event.get("loaded_in_4bit") is True
            and event.get("quantization") == "nf4-double"
            for event in resources
        )
        case["trace"] = {
            "matched": bool(trace),
            "three_stage_calls_observed": confirmed,
            "nf4_runtime_observed": quantized,
            "record": trace,
            "read_error": error,
        }
        if required and not skips_model:
            case["checks"]["local_three_stage_trace"] = confirmed
            case["checks"]["nf4_runtime_trace"] = quantized
            case["passed"] = case["passed"] and confirmed and quantized
            if not confirmed or not quantized:
                case["error"] = (
                    case.get("error", "")
                    + " local 3단계 또는 NF4 실행 진단이 부족합니다."
                ).strip()
    model_cases = [
        case
        for case in report["cases"]
        if case.get("expected_neutral_category") != "out_of_scope"
    ]
    if model_cases and all(
        case["trace"]["nf4_runtime_observed"] for case in model_cases
    ):
        report["quantization"] = {
            "status": "nf4_observed_in_server_runtime_trace",
            "explanation": "요청 ID가 일치하는 서버 model_resources 진단에서 4-bit NF4 double quantization을 확인했습니다.",
        }
    else:
        report["quantization"] = {
            "status": "not_confirmed_in_runtime_trace",
            "explanation": "모델을 호출하는 검사 사례의 NF4 실행 진단이 확인되지는 않았습니다.",
        }
    report["passed"] = report["passed"] and all(
        case["passed"] for case in report["cases"]
    )
