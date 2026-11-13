"""실서버 검사 도구의 판정·오류 기록·비밀값 마스킹을 GPU 없이 검사한다."""

import json

import httpx
from fastapi import HTTPException

from app.config import PROJECT_ROOT
from app.dialogue.schemas import CharacterReplyResponse
from scripts.test_llm_api_live import LiveLlmTester, attach_traces
from conftest import TOKEN


def runner(client):
    """네트워크 대신 임시 FastAPI fixture로 요청을 전달한다."""
    def send(request):
        response = client.request(request.method, str(request.url), content=request.content,
                                  headers=dict(request.headers))
        return httpx.Response(response.status_code, headers=response.headers, content=response.content)
    return LiveLlmTester(httpx.Client(base_url="http://testserver", transport=httpx.MockTransport(send)),
                         TOKEN, PROJECT_ROOT / "data")


class StubGraph:
    """모델이 아닌 도구 검사용 stop 응답. 실제 GPU 실행 증거가 아니다."""

    async def generate(self, request):
        """승인 문장을 반환해 HTTP 저장·보고서 계약만 검사한다."""
        return CharacterReplyResponse(request_id=request.request_id, suspect_id=request.suspect_id,
            state_revision=request.state_revision, reply=" ".join(f.text for f in request.allowed_facts),
            used_fact_ids=[f.id for f in request.allowed_facts], model_version="Qwen2.5-7B-Instruct-nf4+test-adapter",
            finish_reason="stop")


def test_live_runner_rejects_fixture_200(client):
    """200이어도 fixed 응답은 실제 LLM 성공으로 오인하지 않는다."""
    tester = runner(client)
    report = tester.run(["profile"])
    assert not report["passed"]
    case = report["cases"][0]
    assert not case["checks"]["generated_stop"]
    assert not case["checks"]["non_fixture_version"]
    assert [row["purpose"] for row in case["exchanges"]].count("llm_under_test") == 1
    sanitized = json.dumps(tester.redact(report), ensure_ascii=False)
    assert all(secret not in sanitized for secret in tester.secrets)


def test_live_runner_selected_cases_and_commit_checks(client, monkeypatch):
    """선택한 심문만 실행하고 버전·대화·쟁점·복원까지 확인한다."""
    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service, "graph", StubGraph())
    tester = runner(client)
    report = tester.run(["profile", "evidence"])
    assert report["passed"], report
    assert len(report["cases"]) == 2
    assert all(all(case["checks"].values()) for case in report["cases"])
    targets = [row for case in report["cases"] for row in case["exchanges"] if row["purpose"] == "llm_under_test"]
    assert len(targets) == 2
    assert all(row["input"]["path"].endswith("/interrogations") for row in targets)
    assert report["cases"][1]["checks"]["finding_committed"]
    assert report["quantization"]["status"] == "not_measured_via_http"


def test_live_runner_generation_failure_keeps_error_and_input(client, monkeypatch):
    """검증 오류 코드·질문·UUID를 오류 후에도 보존한다."""
    class BrokenGraph:
        """모델 검증 실패 응답을 재현한다."""
        async def generate(self, request):
            raise HTTPException(502, "Generation service failed", headers={"X-Generation-Error": "invalid_verification_output"})
    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service, "graph", BrokenGraph())
    case = runner(client).run(["profile"])["cases"][0]
    assert not case["passed"]
    exchange = case["exchanges"][-1]
    assert exchange["output"]["status"] == 502
    assert exchange["output"]["generation_error"] == "invalid_verification_output"
    assert exchange["input"]["body"]["request_id"] == case["request_id"]
    assert exchange["input"]["body"]["question"]


def test_live_runner_requires_matching_local_trace_and_nf4(client, monkeypatch, tmp_path):
    """버전 이름만으로 NF4를 확정하지 않고 해당 요청의 실행 진단을 요구한다."""
    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service, "graph", StubGraph())
    report = runner(client).run(["profile"])
    path = tmp_path / "trace.jsonl"
    trace = {"request_id": report["cases"][0]["request_id"], "settings": {"generation_mode": "local"},
             "events": [{"stage": key} for key in ("retrieval", "generation", "verification")] + [
                 {"stage": "model_resources", "loaded_in_4bit": True, "quantization": "nf4-double"}]}
    path.write_text(json.dumps(trace) + "\n")
    attach_traces(report, path, required=True)
    assert report["passed"]
    assert report["quantization"]["status"] == "nf4_observed_in_server_runtime_trace"
    attach_traces(report, tmp_path / "missing.jsonl", required=True)
    assert not report["passed"]
    assert not report["cases"][0]["checks"]["nf4_runtime_trace"]


def test_live_runner_timeout_preserves_uuid_without_automatic_retry(client):
    """시간 초과의 모호한 결과를 성공으로 바꾸거나 새 UUID로 몰래 재전송하지 않는다."""
    attempts = []

    def send(request):
        if request.url.path.endswith('/interrogations'):
            attempts.append(json.loads(request.content))
            raise httpx.ReadTimeout('simulated timeout', request=request)
        response = client.request(request.method, str(request.url), content=request.content,
                                  headers=dict(request.headers))
        return httpx.Response(response.status_code, headers=response.headers, content=response.content)

    tester = LiveLlmTester(httpx.Client(base_url='http://testserver', transport=httpx.MockTransport(send)),
                          TOKEN, PROJECT_ROOT / 'data')
    case = tester.run(['profile'])['cases'][0]
    assert not case['passed']
    assert len(attempts) == 1
    assert attempts[0]['request_id'] == case['request_id']
    assert case['exchanges'][-1]['transport_error'] == 'ReadTimeout'
    assert case['exchanges'][-1]['output'] is None
