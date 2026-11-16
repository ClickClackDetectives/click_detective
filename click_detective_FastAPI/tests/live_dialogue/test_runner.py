"""live_dialogue/test_runner.py의 회귀 동작을 확인한다."""

import json

import httpx
from fastapi import HTTPException

from app.config import PROJECT_ROOT
from app.dialogue.schemas import CharacterReplyResponse
from scripts.test_llm_api_live import LiveLlmTester
from tests.conftest import TOKEN


def runner(client):
    """네트워크 대신 임시 FastAPI fixture로 요청을 전달한다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.

    Returns:
        LiveLlmTester: 네트워크 대신 테스트 앱을 호출하는 실서버 검사기.
    """

    def send(request):
        """실서버 검사기의 요청을 테스트 클라이언트로 전달한다.

        Args:
            request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

        Returns:
            httpx.Response: 테스트 앱의 상태 코드·헤더·본문을 옮긴 HTTP 응답.
        """
        response = client.request(
            request.method,
            str(request.url),
            content=request.content,
            headers=dict(request.headers),
        )
        return httpx.Response(
            response.status_code, headers=response.headers, content=response.content
        )

    return LiveLlmTester(
        httpx.Client(base_url="http://testserver", transport=httpx.MockTransport(send)),
        TOKEN,
        PROJECT_ROOT / "data",
    )


class StubGraph:
    """모델이 아닌 도구 검사용 stop 응답. 실제 GPU 실행 증거가 아니다.

    Args:
        없음.

    Returns:
        StubGraph: 위 역할을 수행하도록 생성된 객체.
    """

    async def generate(self, request):
        """승인 문장을 반환해 HTTP 저장·보고서 계약만 검사한다.

        Args:
            request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

        Returns:
            str: 호출 목적에 맞게 생성한 모델 출력 원문.
        """
        return CharacterReplyResponse(
            request_id=request.request_id,
            suspect_id=request.suspect_id,
            state_revision=request.state_revision,
            reply=" ".join(f.text for f in request.allowed_facts),
            used_fact_ids=[f.id for f in request.allowed_facts],
            model_version="Qwen2.5-7B-Instruct-nf4+test-adapter",
            finish_reason="stop",
        )


def test_live_runner_rejects_fixture_200(client):
    """200이어도 fixed 응답은 실제 LLM 성공으로 오인하지 않는다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
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
    """선택한 심문만 실행하고 버전·대화·쟁점·복원까지 확인한다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.
        monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service, "graph", StubGraph())
    tester = runner(client)
    report = tester.run(["profile", "evidence"])
    assert report["passed"], report
    assert len(report["cases"]) == 2
    assert all(all(case["checks"].values()) for case in report["cases"])
    targets = [
        row
        for case in report["cases"]
        for row in case["exchanges"]
        if row["purpose"] == "llm_under_test"
    ]
    assert len(targets) == 2
    assert all(row["input"]["path"].endswith("/interrogations") for row in targets)
    assert report["cases"][1]["checks"]["finding_committed"]
    assert report["quantization"]["status"] == "not_measured_via_http"


def test_live_runner_generation_failure_keeps_error_and_input(client, monkeypatch):
    """검증 오류 코드·질문·UUID를 오류 후에도 보존한다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.
        monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """

    class BrokenGraph:
        """모델 검증 실패 응답을 재현한다.

        Args:
            없음.

        Returns:
            BrokenGraph: 위 역할을 수행하도록 생성된 객체.
        """

        async def generate(self, request):
            """호출 목적에 맞는 모델 출력을 만들거나 검사용 실패를 발생시킨다.

            Args:
                request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

            Returns:
                str: 호출 목적에 맞게 생성한 모델 출력 원문.
            """
            raise HTTPException(
                502,
                "Generation service failed",
                headers={"X-Generation-Error": "invalid_verification_output"},
            )

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
