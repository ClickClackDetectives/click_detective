"""live_dialogue/test_trace_and_timeout.py의 회귀 동작을 확인한다."""

import json

import httpx

from app.config import PROJECT_ROOT
from scripts.test_llm_api_live import LiveLlmTester, attach_traces
from tests.conftest import TOKEN

from .test_runner import StubGraph, runner


def test_live_runner_requires_matching_local_trace_and_nf4(
    client, monkeypatch, tmp_path
):
    """버전 이름만으로 NF4를 확정하지 않고 해당 요청의 실행 진단을 요구한다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.
        monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.
        tmp_path: pytest가 제공하는 테스트별 임시 디렉터리.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service, "graph", StubGraph())
    report = runner(client).run(["profile"])
    path = tmp_path / "trace.jsonl"
    trace = {
        "request_id": report["cases"][0]["request_id"],
        "settings": {"generation_mode": "local"},
        "events": [
            {"stage": key} for key in ("retrieval", "generation", "verification")
        ]
        + [
            {
                "stage": "model_resources",
                "loaded_in_4bit": True,
                "quantization": "nf4-double",
            }
        ],
    }
    trace["events"].extend(
        {"stage": "agent_timing", "agent": agent, "elapsed_ms": duration}
        for agent, duration in (
            ("preprocess_agent", 1.25),
            ("inference_agent", 20),
            ("validation_agent", 8),
            ("inference_agent", 15.5),
            ("validation_agent", 7),
        )
    )
    path.write_text(json.dumps(trace) + "\n")
    attach_traces(report, path, required=True)
    assert report["passed"]
    assert report["quantization"]["status"] == "nf4_observed_in_server_runtime_trace"
    assert report["cases"][0]["agent_timings"] == {
        "preprocess_agent": {"calls_ms": [1.25], "total_ms": 1.25},
        "inference_agent": {"calls_ms": [20, 15.5], "total_ms": 35.5},
        "validation_agent": {"calls_ms": [8, 7], "total_ms": 15},
    }
    attach_traces(report, tmp_path / "missing.jsonl", required=True)
    assert not report["passed"]
    assert not report["cases"][0]["checks"]["nf4_runtime_trace"]
    assert report["cases"][0]["agent_timings"] == {}


def test_live_runner_timeout_preserves_uuid_without_automatic_retry(client):
    """시간 초과의 모호한 결과를 성공으로 바꾸거나 새 UUID로 몰래 재전송하지 않는다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    attempts = []

    def send(request):
        """실서버 검사기의 요청을 테스트 클라이언트로 전달한다.

        Args:
            request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

        Returns:
            httpx.Response: 테스트 앱의 상태 코드·헤더·본문을 옮긴 HTTP 응답.
        """
        if request.url.path.endswith("/interrogations"):
            attempts.append(json.loads(request.content))
            raise httpx.ReadTimeout("simulated timeout", request=request)
        response = client.request(
            request.method,
            str(request.url),
            content=request.content,
            headers=dict(request.headers),
        )
        return httpx.Response(
            response.status_code, headers=response.headers, content=response.content
        )

    tester = LiveLlmTester(
        httpx.Client(base_url="http://testserver", transport=httpx.MockTransport(send)),
        TOKEN,
        PROJECT_ROOT / "data",
    )
    case = tester.run(["profile"])["cases"][0]
    assert not case["passed"]
    assert len(attempts) == 1
    assert attempts[0]["request_id"] == case["request_id"]
    assert case["exchanges"][-1]["transport_error"] == "ReadTimeout"
    assert case["exchanges"][-1]["output"] is None
