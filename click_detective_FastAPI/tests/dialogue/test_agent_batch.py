"""실서버 에이전트 검사 입력과 순차 보고서를 확인한다."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx

from app.dialogue.dto.dialogue_reply_dto import CharacterReplyRequest
from app.runtime.runtime_settings import PROJECT_ROOT
from scripts import test_llm_api_live as cli
from scripts.live_dialogue.agent_inputs import NEUTRAL_QUESTIONS, load_agent_inputs
from scripts.test_llm_api_live import LiveLlmTester


def test_agent_batch_records_inputs_through_a_failed_case():
    """기본 입력 132건을 순차 요청하고 중간 오류 다음 사례도 기록한다.

    Args:
        없음.

    Returns:
        None: 입력 다양성과 요청별 성공·실패 기록을 검사한다.
    """
    inputs = load_agent_inputs(None)
    wire_inputs = [
        {
            key: value
            for key, value in body.items()
            if key != "expected_neutral_category"
        }
        for body in inputs
    ]
    requests = [CharacterReplyRequest.model_validate(body) for body in wire_inputs]
    assert len(requests) == 132
    assert len({request.request_id for request in requests}) == 132
    assert len({(request.suspect_id, request.question) for request in requests}) == 132
    assert {len(request.required_fact_ids) for request in requests} == {0, 1, 2, 3}
    assert any(request.history for request in requests)
    assert any(request.presented_materials for request in requests)
    seen = []

    def send(request):
        """한 사례에만 HTTP 오류를 반환하고 다른 사례는 정상 응답한다.

        Args:
            request: 검사기가 전송한 HTTP 요청.

        Returns:
            httpx.Response: 오류 응답 또는 해당 입력과 일치하는 모의 응답.
        """
        assert request.method == "POST"
        assert request.url.path == "/internal/agent-test"
        body = json.loads(request.content)
        seen.append(body)
        if len(seen) == 60:
            return httpx.Response(502, json={"detail": "simulated failure"})
        assert "expected_neutral_category" not in body
        return httpx.Response(
            200,
            json={
                "request_id": body["request_id"],
                "suspect_id": body["suspect_id"],
                "state_revision": body["state_revision"],
                "finish_reason": "stop" if body["allowed_facts"] else "neutral",
                "model_version": "test-model"
                if body["allowed_facts"]
                else "fixed-neutral-v2",
                "reply": "모의 응답",
                "used_fact_ids": body["required_fact_ids"],
            },
        )

    with httpx.Client(
        base_url="http://testserver", transport=httpx.MockTransport(send)
    ) as client:
        report = LiveLlmTester(client, "test-key", PROJECT_ROOT / "data").run_agents(
            inputs
        )

    assert seen == wire_inputs
    assert not report["passed"]
    assert sum(case["passed"] for case in report["cases"]) == 131
    assert report["cases"][59]["exchanges"][0]["output"]["status"] == 502
    assert report["cases"][-1]["name"] == "agents-132"
    assert report["cases"][-1]["passed"]


def test_agent_batch_accepts_json_arrays_and_multiple_files(tmp_path):
    """단일 객체와 대량 배열을 지정 순서대로 읽어 요청 ID를 재발급한다.

    Args:
        tmp_path: 사용자 입력 JSON 예시를 저장할 임시 디렉터리.

    Returns:
        None: 입력 순서와 최대 실행 건수 옵션을 검사한다.
    """
    first, second = load_agent_inputs([], limit=2)
    single = tmp_path / "single.json"
    batch = tmp_path / "batch.json"
    single.write_text(json.dumps(second))
    batch.write_text(json.dumps([first] * 120))
    assert len(load_agent_inputs([single, batch])) == 121
    inputs = load_agent_inputs([single, batch], limit=3)
    assert [row["question"] for row in inputs] == [
        second["question"],
        first["question"],
        first["question"],
    ]
    assert len({row["request_id"] for row in inputs}) == 3
    assert all(
        row["request_id"] not in {first["request_id"], second["request_id"]}
        for row in inputs
    )


def test_batch_writes_inputs_outputs_and_timings(tmp_path, monkeypatch):
    """버전 선택 없이 실행한 배치의 요청과 진단 시간을 저장한다.

    Args:
        tmp_path: 진단과 보고서를 보관할 임시 경로.
        monkeypatch: 네트워크와 환경변수를 모의 값으로 바꾸는 pytest 도구.

    Returns:
        None: 132개 실행 결과와 일치하는 요청별 시간 기록을 확인한다.
    """
    traces = tmp_path / "trace.jsonl"
    path = tmp_path / "report.json"
    agents = ["preprocess_agent", "inference_agent", "validation_agent"]
    categories = {question: category for category, question in NEUTRAL_QUESTIONS}
    sent = []

    def send(request):
        """요청과 같은 식별자를 가진 모의 응답을 반환한다.

        Args:
            request: 검사기가 보낸 HTTP 요청.

        Returns:
            httpx.Response: 서버 설정 또는 그래프 응답.
        """
        assert request.url.path == "/internal/agent-test"
        assert request.method == "POST"
        body = json.loads(request.content)
        sent.append(body)
        trace = {
            "request_id": body["request_id"],
            "events": [
                {"stage": "agent_timing", "agent": agent, "elapsed_ms": 1.25}
                for agent in agents
            ],
        }
        category = categories.get(body["question"])
        if category == "out_of_scope":
            trace["events"] = []
        if category:
            trace["events"].append(
                {"stage": "validation_outcome", "neutral_category": category}
            )
        with traces.open("a") as stream:
            stream.write(json.dumps(trace) + "\n")
        assert "expected_neutral_category" not in body
        return httpx.Response(
            200,
            json={
                "request_id": body["request_id"],
                "suspect_id": body["suspect_id"],
                "state_revision": body["state_revision"],
                "finish_reason": "stop" if body["allowed_facts"] else "neutral",
                "model_version": "test-model"
                if body["allowed_facts"]
                else "fixed-neutral-v2",
                "reply": "모의 응답",
                "used_fact_ids": body["required_fact_ids"],
            },
        )

    client = httpx.Client(
        base_url="http://testserver", transport=httpx.MockTransport(send)
    )
    monkeypatch.setattr(cli, "httpx", SimpleNamespace(Client=Mock(return_value=client)))
    monkeypatch.setenv("CLICK_API_KEY", "test-service-key")
    result = cli.main(
        [
            "--agents-only",
            "--trace-path",
            str(traces),
            "--report",
            str(path),
        ]
    )
    report = json.loads(path.read_text())
    assert "validation_agent_version" not in report
    assert result == 0
    assert len(sent) == len(report["cases"]) == 132
    for body, case in zip(sent, report["cases"], strict=True):
        (exchange,) = case["exchanges"]
        assert exchange["input"]["body"] == body
        assert exchange["output"]["body"]["reply"] == "모의 응답"
        assert exchange["elapsed_ms"] >= 0
        category = categories.get(body["question"])
        timings = set() if category == "out_of_scope" else set(agents)
        assert set(case["agent_timings"]) == timings
        if category:
            assert case["expected_neutral_category"] == category
            assert case["checks"]["expected_neutral_category"]
            assert case["checks"]["neutral_no_used_facts"]
