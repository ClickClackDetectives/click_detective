"""130개 대화 사례의 JSON과 발표용 문서를 갱신한다."""

import json
from collections import Counter
from datetime import datetime, timezone

from .examples import BACKUP, DOCUMENT, REPORT


def save(tester, finished=False):
    """비밀값을 가리고 JSON과 읽기 쉬운 문서를 매 사례마다 원자적으로 갱신한다.

    Args:
        tester: 검사 사례와 HTTP 기록을 관리하는 실서버 테스트 객체.
        finished: 모든 실서버 검사 사례가 완료되었는지 여부.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    report = tester.report
    report["completed_at"] = (
        (report.get("completed_at") or datetime.now(timezone.utc).isoformat())
        if finished
        else None
    )
    report["execution_status"] = "completed" if finished else "running"
    report["planned_count"] = 130
    report["completed_count"] = len(report["cases"])
    report["passed"] = (
        finished
        and len(report["cases"]) == 130
        and all(c["passed"] for c in report["cases"])
    )
    outcomes = Counter()
    statuses = Counter()
    for case in report["cases"]:
        exchange = next(
            (e for e in case["exchanges"] if e["purpose"] == "llm_under_test"), {}
        )
        response = exchange.get("output") or {}
        statuses[str(response.get("status", "no_response"))] += 1
        outcomes[
            (response.get("body") or {}).get("result", {}).get("finish_reason", "error")
        ] += 1
    report["summary"] = {
        "http_status_counts": dict(statuses),
        "finish_reason_counts": dict(outcomes),
        "strict_pass_count": sum(c["passed"] for c in report["cases"]),
        "nf4_observed_case_count": sum(
            bool((c.get("trace") or {}).get("nf4_runtime_observed"))
            for c in report["cases"]
        ),
    }
    observed = report["summary"]["nf4_observed_case_count"]
    report["quantization"] = {
        "status": "nf4_observed_in_all_request_traces"
        if observed == len(report["cases"]) and observed
        else "nf4_observed_in_some_request_traces"
        if observed
        else "not_confirmed_in_runtime_trace",
        "observed_cases": observed,
        "explanation": "요청 ID가 일치하는 NF4 double quantization 진단을 집계했습니다. fixed 경로는 모델 호출 없이 응답할 수 있습니다.",
    }
    clean = tester.redact(report)
    REPORT.parent.mkdir(exist_ok=True)
    temporary = REPORT.with_suffix(".tmp")
    temporary.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + "\n")
    temporary.chmod(0o600)
    temporary.replace(REPORT)
    passed = sum(c["passed"] for c in clean["cases"])
    text = f"""# click_detective 검증 에이전트 실제 서버 입력·출력 예시 130선

사용자가 실행한 `http://127.0.0.1:8000`에 실제 HTTP 요청을 보낸 기록입니다. 기존 내부 함수·모의 모델 130개는 [원본 예시집]({BACKUP.name})으로 보관하고, 이 문서는 실제 게임 질문 130개로 다시 구성했습니다. 기존 내부 검사 번호와 일대일로 같은 검사를 수행한 것은 아닙니다.

- 실행 상태: **{clean["execution_status"]}**
- 완료: {len(clean["cases"])}/130, 엄격한 실모델 검사 통과: {passed}, 실패: {len(clean["cases"]) - passed}
- 시작(UTC): {clean["started_at"]}, 종료(UTC): {clean["completed_at"]}
- 한국 시간은 UTC에 9시간을 더합니다.
- [전체 입력·출력 JSON](click_detective/.reports/llm-api-130-live.json)

## 전체 결과 집계

| 항목 | 개수 |
| --- | ---: |
| HTTP 200 | {statuses.get("200", 0)} |
| stop: 생성·검증 성공 | {outcomes.get("stop", 0)} |
| fixed: 승인 사실 없음 등으로 고정 응답 | {outcomes.get("fixed", 0)} |
| fallback: 생성 경로 실패 후 승인 원문 복구 | {outcomes.get("fallback", 0)} |
| 동일 요청의 NF4 실행 진단 확인 | {clean["summary"]["nf4_observed_case_count"]} |

**130개를 모두 서버에서 실행했다는 뜻이며, 130개 모두 GPU를 호출했다는 뜻은 아닙니다.** 공개할 사실이 없는 fixed 경로에서는 모델을 호출하지 않습니다. strict PASS는 실제 생성·검증과 NF4·어댑터 진단까지 확인한 경우입니다. 실제 응답을 GPU 성공처럼 바꾸지 않았습니다.

## 다시 실행하기

실제 모델 서버가 켜진 상태에서 다음 명령을 실행합니다. 모델을 별도로 로딩하거나 학습하지 않습니다. 새 테스트 수사 130개가 생성되고 이 문서와 JSON은 새 결과로 덮어써집니다.

```bash
cd ~/reverse/click_detective
.cd_venv/bin/python -u scripts/run_130_live_examples.py
```

종료 코드 0은 130개 모두 엄격한 실모델 검사를 통과했다는 뜻입니다. 코드 1은 fixed·fallback 등을 포함해 통과하지 않은 사례가 있다는 뜻이며, 실행 도중 중단됐다는 뜻과 구분해야 합니다. 완료 여부는 execution_status와 completed_count로 확인합니다.

## 읽는 방법

인물 5명 × 26개 질문입니다. 인물마다 소개 3개, 동선 4개, 타인 관련 8개, 원본 추천 질문 3개, 자료 한 개 제시 8개입니다. 실제 카탈로그와 백엔드 사건 데이터를 사용했습니다. 각 사례는 독립된 새 수사이며, 해당 인물과 관련된 1차 쟁점 자료를 미리 열람합니다. 열람은 인물에게 제시한 것과 다르며 쟁점 공개를 자동 보장하지 않습니다. 자료 제시는 한 번에 한 개입니다. 따라서 아무 자료도 열람하지 않은 초기 화면과는 승인 조건이 다를 수 있습니다.

`stop`과 실제 모델·NF4·세 단계 진단·어댑터·저장 검사를 함께 통과해야 PASS입니다. HTTP 200 `fallback`은 플레이 복구가 성공한 것이지만 실제 생성 대사 검사는 FAIL로 기록합니다. 출력과 실패를 임의로 바꾸거나 성공할 때까지 자동 재요청하지 않습니다. HTTP 오류도 실제 결과로 남깁니다.

검증 에이전트 판정 JSON 전문은 서버가 기록하지 않으면 볼 수 없습니다. 아래 진단 이벤트는 실제 기록이며 빠진 판정표를 만들어 넣지 않았습니다. 이 실행은 내부 오류 주입 검사나 정답을 독립 판정하는 사람의 검수를 대신하지 않습니다. GPU 제품명은 보고서가 측정하지 않습니다.

원본 JSON에는 준비 API와 복원 응답을 포함한 전체 상태가 있습니다. 아래는 심문 본문·응답 핵심·같은 요청의 실행 진단을 표시합니다. 인증 키와 수사 토큰은 가렸습니다.

"""
    for i, case in enumerate(clean["cases"], 1):
        exchange = next(
            (e for e in case["exchanges"] if e["purpose"] == "llm_under_test"), None
        )
        text += f"## 예시 {i:03d}. {case['description']}\n\n**결과: {'PASS' if case['passed'] else 'FAIL'}**\n\n"
        if exchange:
            response = exchange.get("output")
            excerpt = response
            if (
                response
                and isinstance(response.get("body"), dict)
                and "state" in response["body"]
            ):
                body = response["body"]
                state = body["state"]
                excerpt = {
                    "status": response["status"],
                    "generation_error": response["generation_error"],
                    "request_id": body.get("request_id"),
                    "result": body.get("result"),
                    "state_excerpt": {
                        k: state.get(k)
                        for k in [
                            "revision",
                            "questions",
                            "findingDetails",
                            "statements",
                        ]
                    },
                }
            text += (
                "**실제 입력**\n\n```json\n"
                + json.dumps(exchange["input"], ensure_ascii=False, indent=2)
                + "\n```\n\n"
            )
            text += (
                "**실제 출력 발췌**\n\n```json\n"
                + json.dumps(
                    {
                        "response": excerpt,
                        "transport_error": exchange.get("transport_error"),
                        "elapsed_ms": exchange["elapsed_ms"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n```\n\n"
            )
        outcome = (
            ((exchange or {}).get("output") or {})
            .get("body", {})
            .get("result", {})
            .get("finish_reason")
        )
        explanation = {
            "stop": "실제 생성 대사가 검증되고 저장됐습니다. 아래 checks와 서버 진단에서 NF4·어댑터 적용 여부도 확인합니다.",
            "fixed": "서버가 공개 가능한 승인 사실을 선택하지 못해 중립 고정 답변을 반환했습니다. GPU 생성이나 의미 검증 성공 사례가 아닙니다. trace 부재는 이 경로의 결과이며 곧바로 양자화 고장이라는 뜻은 아닙니다.",
            "fallback": "생성·검증 경로에서 후보를 최종 승인하지 못해 승인 원문으로 복구했습니다. 실제 사용자 응답과 저장은 이루어졌지만 모델 생성 품질 검사는 통과하지 않았습니다.",
        }.get(outcome, "HTTP 오류 또는 응답 형식을 원본 JSON에서 확인하세요.")
        text += "**해설:** " + explanation + "\n\n"
        text += (
            "**검사 결과와 서버 진단**\n\n```json\n"
            + json.dumps(
                {
                    "checks": case["checks"],
                    "error": case.get("error"),
                    "trace": case.get("trace"),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n```\n\n"
        )
    tmp = DOCUMENT.with_suffix(".tmp")
    tmp.write_text(text)
    tmp.replace(DOCUMENT)
