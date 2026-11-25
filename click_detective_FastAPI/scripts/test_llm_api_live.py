"""실행 중인 FastAPI 대화 경로를 HTTP로 검사하는 명령행 진입점이다."""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from dotenv import dotenv_values

if __package__:
    from .live_dialogue.agent_inputs import load_agent_inputs
    from .live_dialogue.errors import LiveTestFailure as LiveTestFailure
    from .live_dialogue.tester import LiveLlmTester
    from .live_dialogue.traces import attach_traces
else:
    from live_dialogue.agent_inputs import load_agent_inputs
    from live_dialogue.errors import LiveTestFailure as LiveTestFailure
    from live_dialogue.tester import LiveLlmTester
    from live_dialogue.traces import attach_traces

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASE_NAMES = ("profile", "movement", "evidence")


def parser():
    """비밀 키는 명령행 인수가 아닌 환경변수 또는 .env에서만 읽는다.

    Args:
        없음.

    Returns:
        argparse.ArgumentParser: 실서버 검사에 사용할 명령행 인수 파서.
    """
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--backend-url", default="http://127.0.0.1:8000")
    result.add_argument(
        "--case",
        action="append",
        choices=CASE_NAMES,
        dest="cases",
        help="여러 번 지정 가능. 생략하면 3개 전부 검사",
    )
    result.add_argument(
        "--timeout", type=float, default=240, help="요청별 초 단위 대기시간"
    )
    result.add_argument(
        "--agents-only", action="store_true", help="게임 API 없이 대화 에이전트만 검사"
    )
    result.add_argument(
        "--agent-input",
        type=Path,
        action="append",
        help="객체 또는 객체 배열을 담은 입력 JSON 파일. 여러 번 지정 가능",
    )
    result.add_argument(
        "--agent-limit", type=int, help="agents-only 검사에서 실행할 최대 입력 수"
    )
    result.add_argument("--report", type=Path, help="결과 JSON 경로")
    result.add_argument("--env-file", type=Path, default=PROJECT_ROOT / ".env")
    result.add_argument("--data-dir", type=Path, default=PROJECT_ROOT / "data")
    result.add_argument("--api-key-env", default="CLICK_API_KEY")
    result.add_argument(
        "--expected-model-version", help="서버가 보고한 모델 버전의 정확한 일치 검사"
    )
    result.add_argument(
        "--validation-version",
        choices=("v2.1", "v2.2"),
        help="에이전트 배치 실행 전에 확인할 실제 서버의 검증 버전",
    )
    result.add_argument(
        "--trace-path", type=Path, help="같은 실행 서버의 diagnostics JSONL 파일"
    )
    result.add_argument(
        "--require-trace",
        action="store_true",
        help="local 실행과 기대 중립 분류의 진단을 성공 필수 조건으로 검사",
    )
    return result


def run_agents_for_version(tester, inputs, version):
    """버전이 일치하는 서버에서만 에이전트 요청을 시작한다.

    Args:
        tester: 현재 서버의 실서버 검사기.
        inputs: 검사할 입력의 순서 있는 목록.
        version: 확인해야 할 서버 버전. None이면 기존 방식으로 실행한다.

    Returns:
        dict: 배치 결과 또는 사전 확인이 실패한 보고서.
    """
    if version:
        report = tester.report
        report["expected_validation_agent_version"] = version
        report["mode"] = "live_agents_only"
        report["target_api"] = "POST /internal/agent-test"
        try:
            config = tester.exchange(
                report["preparation"], "GET", "/internal/agent-test"
            )
            observed = config.get("validation_agent_version")
            report["validation_agent_version"] = observed
            if observed != version:
                raise LiveTestFailure(
                    f"서버 검증 버전 불일치 (기대 {version}, 실제 {observed})"
                )
            if config.get("diagnostics_enabled") is not True:
                raise LiveTestFailure("서버의 대화 실행 진단이 비활성화되어 있습니다.")
        except LiveTestFailure as error:
            report["error"] = str(error)
            return report
    return tester.run_agents(inputs, progress=True)


def main(argv=None):
    """실행 결과를 JSON으로 저장하고 성공 0·실패 1·설정 오류 2를 반환한다.

    POSIX에서는 결과 파일 권한을 600으로 제한한다.

    Args:
        argv: 명령행 인수 목록. None이면 실제 명령행에서 읽는다.

    Returns:
        int: 성공은 0, 검사 실패는 1. 잘못된 설정은 파서가 오류로 종료한다.
    """
    arguments = parser()
    args = arguments.parse_args(argv)
    url = urlsplit(args.backend_url)
    if (
        url.scheme not in {"http", "https"}
        or not url.hostname
        or url.username
        or url.password
        or url.query
        or url.fragment
        or url.path not in {"", "/"}
    ):
        arguments.error(
            "backend-url은 인증정보·쿼리·하위 경로가 없는 HTTP(S) 서버 주소여야 합니다."
        )
    if args.timeout <= 0 or not args.timeout < float("inf"):
        arguments.error("timeout은 0보다 큰 유한한 초 값이어야 합니다.")
    if args.require_trace and not args.trace_path:
        arguments.error("require-trace에는 trace-path가 필요합니다.")
    if args.validation_version and (not args.agents_only or not args.trace_path):
        arguments.error("validation-version에는 agents-only와 trace-path가 필요합니다.")
    if (args.agent_input or args.agent_limit is not None) and not args.agents_only:
        arguments.error("agent-input과 agent-limit은 agents-only와 함께 사용하세요.")
    if args.agent_limit is not None and args.agent_limit < 1:
        arguments.error("agent-limit은 1 이상이어야 합니다.")
    if args.agents_only and args.cases:
        arguments.error("agents-only에서는 case 옵션을 사용할 수 없습니다.")
    if args.report is None:
        name = (
            f"llm-agents-{args.validation_version}-live.json"
            if args.validation_version
            else "llm-api-live.json"
        )
        args.report = PROJECT_ROOT / ".reports" / name
    if args.report.suffix.lower() != ".json":
        arguments.error("report에는 .json 파일을 지정하세요.")
    agent_inputs = None
    if args.agents_only:
        try:
            agent_inputs = load_agent_inputs(args.agent_input, args.agent_limit)
        except (OSError, ValueError) as error:
            arguments.error(f"agent-input JSON을 읽을 수 없습니다: {error}")
    key = os.environ.get(args.api_key_env) or dotenv_values(args.env_file).get(
        args.api_key_env
    )
    if not key:
        arguments.error(
            f"{args.api_key_env} 환경변수 또는 env-file에 API 키를 설정하세요."
        )
    # 프록시 환경변수로 localhost 요청이나 비밀 헤더가 다른 서버로 전달되지 않게 한다.
    with httpx.Client(
        base_url=args.backend_url.rstrip("/"),
        timeout=args.timeout,
        trust_env=False,
        follow_redirects=False,
    ) as client:
        tester = LiveLlmTester(client, key, args.data_dir, args.expected_model_version)
        if agent_inputs is not None:
            report = run_agents_for_version(
                tester, agent_inputs, args.validation_version
            )
        else:
            report = tester.run(list(dict.fromkeys(args.cases or CASE_NAMES)))
    if args.trace_path:
        attach_traces(report, args.trace_path, args.require_trace)
    report = tester.redact(report)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(args.report, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        if hasattr(os, "fchmod"):
            os.fchmod(stream.fileno(), 0o600)
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    for case in report["cases"]:
        print(
            f"{'PASS' if case['passed'] else 'FAIL'} {case['name']}: {case.get('error') or case['description']}"
        )
    if report.get("error"):
        print("준비 실패:", report["error"])
    print(
        f"심문 사례: {sum(case['passed'] for case in report['cases'])}/{len(report['cases'])} 성공"
    )
    print("JSON 보고서:", args.report)
    print("양자화 확인:", report["quantization"]["status"])
    print(
        "HTTP 결과만으로 양자화가 입증되는 것은 아닙니다. 실행 진단은 --trace-path로 연결하세요."
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
