"""실행 중인 서버에 130개 대화 사례를 순서대로 요청한다."""

import os
import shutil
import sys

import httpx
from dotenv import dotenv_values

if __package__:
    from .live_dialogue.example_reports import save
    from .live_dialogue.examples import BACKUP, DOCUMENT, ROOT, definitions
    from .test_llm_api_live import LiveLlmTester, attach_traces
else:
    from live_dialogue.example_reports import save
    from live_dialogue.examples import BACKUP, DOCUMENT, ROOT, definitions
    from test_llm_api_live import LiveLlmTester, attach_traces


def main():
    """한 서버에 순차 요청하여 GPU 모델 중복 로딩과 동시 부하를 피한다.

    Args:
        없음.

    Returns:
        int: 성공은 0, 검사 실패는 1. 잘못된 설정은 파서가 오류로 종료한다.
    """
    if not BACKUP.exists():
        shutil.copy2(DOCUMENT, BACKUP)
    key = os.environ.get("CLICK_API_KEY") or dotenv_values(ROOT / ".env").get(
        "CLICK_API_KEY"
    )
    if not key:
        raise RuntimeError("CLICK_API_KEY 설정 필요")
    with httpx.Client(
        base_url="http://127.0.0.1:8000", timeout=240, trust_env=False
    ) as client:
        tester = LiveLlmTester(client, key, ROOT / "data")
        tester.exchange(tester.report["preparation"], "GET", "/healthz")
        catalog = tester.exchange(tester.report["preparation"], "GET", "/v1/catalog")
        cases = definitions(catalog)
        tester.report["definitions"] = cases
        for i, definition in enumerate(cases, 1):
            tester.run_case(f"example-{i:03d}", definition, catalog)
            case = tester.report["cases"][-1]
            attach_traces(
                {"cases": [case], "passed": case["passed"]},
                ROOT / ".data/dialogue-traces.jsonl",
                required=True,
            )
            resources = [
                e
                for e in (case["trace"]["record"] or {}).get("events", [])
                if e.get("stage") == "model_resources"
            ]
            case["checks"]["adapter_runtime_trace"] = bool(resources) and all(
                e.get("adapter_enabled") is True for e in resources
            )
            case["passed"] = case["passed"] and case["checks"]["adapter_runtime_trace"]
            save(tester)
            print(
                f"{i}/130 {'PASS' if case['passed'] else 'FAIL'} {definition['description']}",
                flush=True,
            )
        save(tester, finished=True)
    return 0 if tester.report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
