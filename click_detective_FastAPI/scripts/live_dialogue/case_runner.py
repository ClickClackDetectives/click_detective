"""독립 수사의 생성, 심문과 저장 결과를 검사한다."""

from uuid import uuid4

from .errors import LiveTestFailure


def run_case(tester, name, definition, catalog):
    """사례마다 독립 수사를 사용해 앞선 대사·질문 횟수의 영향을 줄인다.

    Args:
        tester: 검사 사례와 HTTP 기록을 관리하는 실서버 테스트 객체.
        name: 읽을 파일 또는 실행할 사례의 이름.
        definition: 질문, 준비 자료와 기대 결과를 담은 검사 사례.
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    case = {
        "name": name,
        "description": definition["description"],
        "passed": False,
        "exchanges": [],
        "checks": {},
        "request_id": None,
    }
    tester.report["cases"].append(case)
    try:
        game = tester.exchange(
            case["exchanges"],
            "POST",
            "/v1/games",
            {
                "request_id": str(uuid4()),
                "case_id": catalog["caseId"],
                "scenario_version": catalog["scenarioVersion"],
            },
        )
        token, state = game["game_token"], game["state"]
        base = "/v1/games/" + game["game_id"]
        for key in definition["evidence_ids"]:
            state = tester.exchange(
                case["exchanges"],
                "POST",
                base + "/examinations",
                {
                    "request_id": str(uuid4()),
                    "expected_revision": state["revision"],
                    "evidence_id": key,
                },
                token,
            )["state"]
        case["request_id"] = str(uuid4())
        body = {
            "request_id": case["request_id"],
            "expected_revision": state["revision"],
            **definition["fields"],
        }
        response = tester.exchange(
            case["exchanges"],
            "POST",
            base + "/interrogations",
            body,
            token,
            "llm_under_test",
        )
        result, updated = response["result"], response["state"]
        version = result.get("model_version", "")
        checks = {
            "request_id_matches": response.get("request_id") == body["request_id"],
            "generated_stop": result.get("finish_reason") == "stop",
            "non_fixture_version": isinstance(version, str)
            and bool(version.strip())
            and not any(
                word in version.lower() for word in ("fixture", "fixed", "mock")
            ),
            "reply_present": isinstance(result.get("reply"), str)
            and bool(result["reply"].strip()),
            "used_fact_ids_present": isinstance(result.get("used_fact_ids"), list)
            and bool(result["used_fact_ids"]),
            "one_question_committed": updated["questions"] == state["questions"] + 1,
            "revision_advanced": updated["revision"] > state["revision"],
            "dialogue_pair_committed": len(updated["messages"])
            == len(state["messages"]) + 2,
            "reply_matches_state": bool(updated["messages"])
            and updated["messages"][-1]["text"] == result.get("reply"),
        }
        if tester.expected_model_version:
            checks["expected_model_version"] = version == tester.expected_model_version
        if definition.get("expected_finding"):
            checks["finding_committed"] = any(
                item["title"] == definition["expected_finding"]
                for item in updated["findingDetails"]
            )
        restored = tester.exchange(case["exchanges"], "GET", base, token=token)["state"]
        checks["saved_state_restored"] = restored == updated
        case["checks"] = checks
        case["passed"] = all(checks.values())
        if not case["passed"]:
            case["error"] = "조건 불일치: " + ", ".join(
                key for key, value in checks.items() if not value
            )
    except (LiveTestFailure, KeyError, TypeError, ValueError) as error:
        case["error"] = str(error)
