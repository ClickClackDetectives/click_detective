"""이미 실행 중인 FastAPI의 심문 LLM 경로만 HTTP로 검사한다.

직접 모델을 로딩하거나 서버를 시작하지 않는다. 새 수사·자료 열람은 심문의
준비 단계이며 실제 검증 대상은 interrogations이다. 입력·출력은 비밀값을 지워 저장한다.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from time import perf_counter
from urllib.parse import urlsplit
from uuid import uuid4

import httpx
from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASE_NAMES = ("profile", "movement", "evidence")


class LiveTestFailure(RuntimeError):
    """HTTP 오류 또는 실제 LLM 응답 조건 불일치를 보고서에 남기기 위한 예외."""


class LiveLlmTester:
    """새 테스트 수사를 만들고 심문 요청·응답·저장 결과를 순서대로 검사한다."""

    def __init__(self, client: httpx.Client, api_key: str, data_dir: Path,
                 expected_model_version: str | None = None):
        """HTTP 클라이언트를 외부에서 받아 단위 검사에서는 네트워크 없이 검사할 수 있다."""
        self.client = client
        self.data_dir = data_dir
        self.expected_model_version = expected_model_version
        self.secrets = [api_key]
        self.headers = {"Authorization": "Bearer " + api_key}
        self.report = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "mode": "live_http", "target_api": "POST /v1/games/{game_id}/interrogations",
            "server_started_by_script": False,
            "quantization": {"status": "not_measured_via_http",
                "explanation": "local 서버 로더는 4-bit NF4를 강제하지만 이 HTTP 검사는 GPU 가중치 형식을 직접 측정하지 않습니다."},
            "preparation": [], "cases": [], "passed": False,
        }

    def redact(self, value):
        """헤더·토큰 필드와 문자열에 포함된 실제 비밀값까지 가린다."""
        if isinstance(value, dict):
            return {key: "[REDACTED]" if key.lower() in {
                "authorization", "x-game-token", "game_token", "api_key"}
                else self.redact(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self.redact(item) for item in value]
        if isinstance(value, str):
            for secret in self.secrets:
                if secret:
                    value = value.replace(secret, "[REDACTED]")
        return value

    def exchange(self, rows, method, path, body=None, token=None, purpose="preparation"):
        """assertion 전에 왕복을 기록한다. 타임아웃도 요청 UUID·본문을 남긴다."""
        headers = self.headers | ({"X-Game-Token": token} if token else {})
        row = {"purpose": purpose, "input": {"method": method, "path": path,
               "headers": headers, "body": body}, "output": None}
        rows.append(row)
        started = perf_counter()
        try:
            response = self.client.request(method, path, headers=headers,
                                           **({"json": body} if body is not None else {}))
            try:
                output = response.json()
            except ValueError:
                output = {"text": response.text}
            # 새 수사 응답의 토큰을 report에 보관하기 전에 마스킹 목록에 추가한다.
            if isinstance(output, dict) and isinstance(output.get("game_token"), str):
                self.secrets.append(output["game_token"])
            row["output"] = {"status": response.status_code, "body": output,
                "generation_error": response.headers.get("X-Generation-Error")}
            if response.status_code != 200:
                code = response.headers.get("X-Generation-Error") or (
                    output.get("detail") if isinstance(output, dict) else None)
                raise LiveTestFailure(f"{method} {path}: HTTP {response.status_code}, 원인: {code}")
            if not isinstance(output, dict):
                raise LiveTestFailure("JSON 객체 응답이 아닙니다.")
            return output
        except httpx.RequestError as error:
            row["transport_error"] = type(error).__name__
            raise LiveTestFailure(
                f"{type(error).__name__}: 응답을 확정할 수 없습니다. 기록된 UUID로 서버 상태·진단을 확인하세요."
            ) from error
        finally:
            row["elapsed_ms"] = round((perf_counter() - started) * 1000, 2)

    def definitions(self, catalog):
        """현재 프로젝트의 인물·주제·1차 단일 근거 쟁점으로 3가지 입력을 구성한다."""
        people = catalog["characters"]
        person = people[0]
        movement = next((item for item in people if any(
            topic["id"] == "movement" for topic in item["interviewTopics"])), None)
        if movement is None:
            raise LiveTestFailure("카탈로그에 동선 심문 주제가 없습니다.")
        topic = next(item for item in movement["interviewTopics"] if item["id"] == "movement")
        evidence = json.loads((self.data_dir / "case/evidence.json").read_text(encoding="utf-8"))["records"]
        rules = json.loads((self.data_dir / "case/findings.private.json").read_text(encoding="utf-8"))["rules"]
        initial_ids = {item["id"] for item in evidence if item["phase"] == 1}
        finding = next((item for item in rules if len(item["need"]) == 1
                        and set(item["need"]) <= initial_ids
                        and item["suspectId"] in {p["id"] for p in people}), None)
        if finding is None:
            raise LiveTestFailure("내부 사건 데이터에 1차 단일 근거 심문 항목이 없습니다.")
        return {
            "profile": {"description": "짧은 자기소개: 승인된 인물 정보로 생성·검증",
                "fields": {"suspect_id": person["id"], "question": "자기소개를 해주세요."}, "evidence_ids": []},
            "movement": {"description": "동선 주제: 여러 승인 문장의 생성·검증",
                "fields": {"suspect_id": movement["id"], "question": topic["question"], "topic_id": topic["id"]},
                "evidence_ids": []},
            "evidence": {"description": "자료 제시: 획득 근거로 인정 대사 생성·검증",
                "fields": {"suspect_id": finding["suspectId"],
                           "question": "제시한 자료의 경위를 설명하세요.", "material_id": finding["need"][0]},
                "evidence_ids": finding["need"], "expected_finding": finding["label"]},
        }

    def run_case(self, name, definition, catalog):
        """사례마다 독립 수사를 사용해 앞선 대사·질문 횟수의 영향을 줄인다."""
        case = {"name": name, "description": definition["description"],
                "passed": False, "exchanges": [], "checks": {}, "request_id": None}
        self.report["cases"].append(case)
        try:
            game = self.exchange(case["exchanges"], "POST", "/v1/games", {
                "request_id": str(uuid4()), "case_id": catalog["caseId"],
                "scenario_version": catalog["scenarioVersion"]})
            token, state = game["game_token"], game["state"]
            base = "/v1/games/" + game["game_id"]
            for key in definition["evidence_ids"]:
                state = self.exchange(case["exchanges"], "POST", base + "/examinations", {
                    "request_id": str(uuid4()), "expected_revision": state["revision"],
                    "evidence_id": key}, token)["state"]
            case["request_id"] = str(uuid4())
            body = {"request_id": case["request_id"], "expected_revision": state["revision"],
                    **definition["fields"]}
            response = self.exchange(case["exchanges"], "POST", base + "/interrogations",
                                     body, token, "llm_under_test")
            result, updated = response["result"], response["state"]
            version = result.get("model_version", "")
            checks = {
                "request_id_matches": response.get("request_id") == body["request_id"],
                "generated_stop": result.get("finish_reason") == "stop",
                "non_fixture_version": isinstance(version, str) and bool(version.strip())
                    and not any(word in version.lower() for word in ("fixture", "fixed", "mock")),
                "reply_present": isinstance(result.get("reply"), str) and bool(result["reply"].strip()),
                "used_fact_ids_present": isinstance(result.get("used_fact_ids"), list)
                    and bool(result["used_fact_ids"]),
                "one_question_committed": updated["questions"] == state["questions"] + 1,
                "revision_advanced": updated["revision"] > state["revision"],
                "dialogue_pair_committed": len(updated["messages"]) == len(state["messages"]) + 2,
                "reply_matches_state": bool(updated["messages"])
                    and updated["messages"][-1]["text"] == result.get("reply"),
            }
            if self.expected_model_version:
                checks["expected_model_version"] = version == self.expected_model_version
            if definition.get("expected_finding"):
                checks["finding_committed"] = any(item["title"] == definition["expected_finding"]
                                                  for item in updated["findingDetails"])
            restored = self.exchange(case["exchanges"], "GET", base, token=token)["state"]
            checks["saved_state_restored"] = restored == updated
            case["checks"] = checks
            case["passed"] = all(checks.values())
            if not case["passed"]:
                case["error"] = "조건 불일치: " + ", ".join(key for key, value in checks.items() if not value)
        except (LiveTestFailure, KeyError, TypeError, ValueError) as error:
            case["error"] = str(error)

    def run(self, selected):
        """준비 조회를 한 번 수행하고 선택한 심문 사례만 실행한다."""
        try:
            self.exchange(self.report["preparation"], "GET", "/healthz")
            catalog = self.exchange(self.report["preparation"], "GET", "/v1/catalog")
            definitions = self.definitions(catalog)
            self.report["case_data"] = {"case_id": catalog["caseId"],
                "scenario_version": catalog["scenarioVersion"],
                "sources": ["data/case/evidence.json", "data/case/findings.private.json", "GET /v1/catalog"]}
            for name in selected:
                self.run_case(name, definitions[name], catalog)
        except (LiveTestFailure, OSError, KeyError, TypeError, ValueError) as error:
            self.report["error"] = str(error)
        self.report["passed"] = bool(self.report["cases"]) and all(case["passed"] for case in self.report["cases"])
        self.report["completed_at"] = datetime.now(timezone.utc).isoformat()
        return self.report


def attach_traces(report, trace_path, required=False):
    """같은 서버의 진단 JSONL을 선택적으로 읽어 요청별 3단계 호출 증거를 연결한다."""
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
        confirmed = bool(trace) and (trace.get("settings") or {}).get("generation_mode") == "local" and {
            "retrieval", "generation", "verification"} <= stages
        resources = [event for event in (trace or {}).get("events", [])
                     if event.get("stage") == "model_resources"]
        quantized = bool(resources) and all(event.get("loaded_in_4bit") is True
                      and event.get("quantization") == "nf4-double" for event in resources)
        case["trace"] = {"matched": bool(trace), "three_stage_calls_observed": confirmed,
                         "nf4_runtime_observed": quantized,
                         "record": trace, "read_error": error}
        if required:
            case["checks"]["local_three_stage_trace"] = confirmed
            case["checks"]["nf4_runtime_trace"] = quantized
            case["passed"] = case["passed"] and confirmed and quantized
            if not confirmed or not quantized:
                case["error"] = (case.get("error", "") + " local 3단계 또는 NF4 실행 진단이 부족합니다.").strip()
    if report["cases"] and all(case["trace"]["nf4_runtime_observed"] for case in report["cases"]):
        report["quantization"] = {"status": "nf4_observed_in_server_runtime_trace",
            "explanation": "요청 ID가 일치하는 서버 model_resources 진단에서 4-bit NF4 double quantization을 확인했습니다."}
    else:
        report["quantization"] = {"status": "not_confirmed_in_runtime_trace",
            "explanation": "선택한 모든 심문의 NF4 실행 진단이 확인되지는 않았습니다."}
    report["passed"] = report["passed"] and all(case["passed"] for case in report["cases"])


def parser():
    """비밀 키는 명령행 인수가 아닌 환경변수 또는 .env에서만 읽는다."""
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--backend-url", default="http://127.0.0.1:8000")
    result.add_argument("--case", action="append", choices=CASE_NAMES, dest="cases",
                        help="여러 번 지정 가능. 생략하면 3개 전부 검사")
    result.add_argument("--timeout", type=float, default=240, help="요청별 초 단위 대기시간")
    result.add_argument("--report", type=Path, default=PROJECT_ROOT / ".reports/llm-api-live.json")
    result.add_argument("--env-file", type=Path, default=PROJECT_ROOT / ".env")
    result.add_argument("--data-dir", type=Path, default=PROJECT_ROOT / "data")
    result.add_argument("--api-key-env", default="CLICK_API_KEY")
    result.add_argument("--expected-model-version", help="서버가 보고한 모델 버전의 정확한 일치 검사")
    result.add_argument("--trace-path", type=Path, help="같은 실행 서버의 diagnostics JSONL 파일")
    result.add_argument("--require-trace", action="store_true", help="local 3단계 진단 증거도 성공 필수 조건으로 검사")
    return result


def main(argv=None):
    """실행 결과를 권한 600 JSON으로 저장하고 성공 0·실패 1·설정 오류 2를 반환한다."""
    arguments = parser()
    args = arguments.parse_args(argv)
    url = urlsplit(args.backend_url)
    if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in {"", "/"}:
        arguments.error("backend-url은 인증정보·쿼리·하위 경로가 없는 HTTP(S) 서버 주소여야 합니다.")
    if args.timeout <= 0 or not args.timeout < float("inf"):
        arguments.error("timeout은 0보다 큰 유한한 초 값이어야 합니다.")
    if args.require_trace and not args.trace_path:
        arguments.error("require-trace에는 trace-path가 필요합니다.")
    if args.report.suffix.lower() != ".json":
        arguments.error("report에는 .json 파일을 지정하세요.")
    key = os.environ.get(args.api_key_env) or dotenv_values(args.env_file).get(args.api_key_env)
    if not key:
        arguments.error(f"{args.api_key_env} 환경변수 또는 env-file에 API 키를 설정하세요.")
    # 프록시 환경변수로 localhost 요청이나 비밀 헤더가 다른 서버로 전달되지 않게 한다.
    with httpx.Client(base_url=args.backend_url.rstrip("/"), timeout=args.timeout,
                      trust_env=False, follow_redirects=False) as client:
        tester = LiveLlmTester(client, key, args.data_dir, args.expected_model_version)
        report = tester.run(list(dict.fromkeys(args.cases or CASE_NAMES)))
    if args.trace_path:
        attach_traces(report, args.trace_path, args.require_trace)
    report = tester.redact(report)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(args.report, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    for case in report["cases"]:
        print(f"{'PASS' if case['passed'] else 'FAIL'} {case['name']}: {case.get('error') or case['description']}")
    if report.get("error"):
        print("준비 실패:", report["error"])
    print(f"심문 사례: {sum(case['passed'] for case in report['cases'])}/{len(report['cases'])} 성공")
    print("JSON 보고서:", args.report)
    print("양자화 확인:", report["quantization"]["status"])
    print("HTTP 결과만으로 양자화가 입증되는 것은 아닙니다. 실행 진단은 --trace-path로 연결하세요.")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
