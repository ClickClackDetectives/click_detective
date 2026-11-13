"""모든 테스트는 새 프로젝트 내부 데이터·임시 DB를 사용하고 HTTP 입력·출력을 기록한다."""

import json
from pathlib import Path
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app.config import PROJECT_ROOT, Settings
from app.main import create_app

TOKEN = "click-test-service-secret"


def redact(value):
    """인증·게임 토큰은 JSON 보고서에서 숨긴다. 실제 질문·응답은 보존한다."""
    if isinstance(value, dict):
        return {key: "[REDACTED]" if key.lower() in {"authorization", "x-game-token", "game_token"} else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """검사 결과를 테스트 종료 후 보고서에서 읽을 수 있게 보관한다."""
    outcome = yield
    setattr(item, "report_" + call.when, outcome.get_result())


@pytest.fixture(scope="session")
def results():
    """모든 검사 결과와 HTTP 왕복을 하나의 JSON에 저장한다."""
    rows = []
    yield rows
    target = PROJECT_ROOT / ".reports/pytest.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps({"mode": "fixture", "passed": sum(row["outcome"] == "passed" for row in rows),
        "failed": sum(row["outcome"] == "failed" for row in rows), "tests": rows}, ensure_ascii=False, indent=2))


@pytest.fixture(autouse=True)
def record(request, results):
    """HTTP가 없는 규칙 테스트도 보고서에서 빠뜨리지 않는다."""
    request.node.exchanges = []
    yield
    report = getattr(request.node, "report_call", None) or getattr(request.node, "report_setup", None)
    results.append({"name": request.node.nodeid, "outcome": report.outcome if report else "unknown",
                    "exchanges": request.node.exchanges})


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    """실제 FastAPI를 GPU 없는 명시적 fixture 모드로 실행한다."""
    config = Settings(api_key=TOKEN, generation_mode="fixture", fallback_on_error=False, _env_file=None,
        database_path=tmp_path_factory.mktemp("click-detective") / "test.sqlite3",
        diagnostics_path=tmp_path_factory.mktemp("click-traces") / "trace.jsonl")
    with TestClient(create_app(config)) as instance:
        yield instance


@pytest.fixture
def api(client, request):
    """실제 응답을 assertion 이전에 기록하는 호출 함수를 제공한다."""
    def send(method, path, body=None, game_token=None, authenticated=True, **kwargs):
        """인증과 JSON·미디어 응답을 함께 지원한다."""
        headers = {"Authorization": "Bearer " + TOKEN} if authenticated else {}
        if game_token:
            headers["X-Game-Token"] = game_token
        headers.update(kwargs.pop("headers", {}))
        response = client.request(method, path, json=body, headers=headers, **kwargs)
        try:
            output = response.json()
        except ValueError:
            output = {"content_type": response.headers.get("content-type"), "bytes": len(response.content)}
        request.node.exchanges.append({"input": {"method": method, "path": path, "body": redact(body), "headers": redact(headers)},
            "output": {"status": response.status_code, "body": redact(output)}})
        return response
    return send


@pytest.fixture
def game(api):
    """현재 실제 사건 버전으로 독립 수사를 만든다."""
    catalog = api("GET", "/v1/catalog").json()
    response = api("POST", "/v1/games", {"request_id": str(uuid4()), "case_id": catalog["caseId"], "scenario_version": catalog["scenarioVersion"]})
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture
def play(api, game):
    """상태 변경의 새 revision을 보관하는 실제 게임 API 실행 도우미."""
    class Player:
        """게임 상태를 조작하지 않고 사용자 행동 API로만 진행한다."""
        state = game["state"]
        game_id = game["game_id"]
        token = game["game_token"]

        def act(self, endpoint, **fields):
            """새 요청 UUID·서버 revision을 넣고 갱신 상태를 적용한다."""
            body = {"request_id": str(uuid4()), "expected_revision": self.state["revision"], **fields}
            response = api("PUT" if endpoint == "notes" else "POST", f"/v1/games/{self.game_id}/{endpoint}", body, self.token)
            assert response.status_code == 200, (endpoint, response.text)
            self.state = response.json()["state"]
            return response.json()
    return Player()
