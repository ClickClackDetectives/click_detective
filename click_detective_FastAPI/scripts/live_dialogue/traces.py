"""서버의 대화 생성 진단을 실서버 검사 보고서에 연결한다."""

import json


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
        stages = {event.get("stage") for event in (trace or {}).get("events", [])}
        confirmed = (
            bool(trace)
            and (trace.get("settings") or {}).get("generation_mode") == "local"
            and {"retrieval", "generation", "verification"} <= stages
        )
        resources = [
            event
            for event in (trace or {}).get("events", [])
            if event.get("stage") == "model_resources"
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
        if required:
            case["checks"]["local_three_stage_trace"] = confirmed
            case["checks"]["nf4_runtime_trace"] = quantized
            case["passed"] = case["passed"] and confirmed and quantized
            if not confirmed or not quantized:
                case["error"] = (
                    case.get("error", "")
                    + " local 3단계 또는 NF4 실행 진단이 부족합니다."
                ).strip()
    if report["cases"] and all(
        case["trace"]["nf4_runtime_observed"] for case in report["cases"]
    ):
        report["quantization"] = {
            "status": "nf4_observed_in_server_runtime_trace",
            "explanation": "요청 ID가 일치하는 서버 model_resources 진단에서 4-bit NF4 double quantization을 확인했습니다.",
        }
    else:
        report["quantization"] = {
            "status": "not_confirmed_in_runtime_trace",
            "explanation": "선택한 모든 심문의 NF4 실행 진단이 확인되지는 않았습니다.",
        }
    report["passed"] = report["passed"] and all(
        case["passed"] for case in report["cases"]
    )
