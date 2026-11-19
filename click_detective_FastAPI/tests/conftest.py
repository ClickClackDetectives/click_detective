"""모든 테스트는 새 프로젝트 내부 데이터·임시 DB를 사용하고 HTTP 입력·출력을 기록한다."""

import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.config import PROJECT_ROOT, Settings
from app.main import create_app
from tests.investigation.player import Player

TOKEN = "click-test-service-secret"


def redact(value):
    """인증·게임 토큰은 JSON 보고서에서 숨긴다. 실제 질문·응답은 보존한다.

    Args:
        value: 검사·변환하거나 비밀값을 가릴 입력 값.

    Returns:
        입력과 같은 구조의 값: 인증 정보와 알려진 비밀값을 가린 결과.
    """
    if isinstance(value, dict):
        return {
            key: "[REDACTED]"
            if key.lower() in {"authorization", "x-game-token", "game_token"}
            else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """검사 결과를 테스트 종료 후 보고서에서 읽을 수 있게 보관한다.

    Args:
        item: pytest 검사 항목 또는 처리할 데이터 항목.
        call: pytest가 제공하는 현재 실행 단계의 결과 정보.

    Returns:
        Iterator: with 또는 pytest 실행 동안 필요한 자원을 제공하는 반복자. 종료 시 정리 작업을 수행한다.
    """
    outcome = yield
    setattr(item, "report_" + call.when, outcome.get_result())


@pytest.fixture(scope="session")
def results():
    """모든 검사 결과와 HTTP 왕복을 하나의 JSON에 저장한다.

    Args:
        없음.

    Returns:
        Iterator: with 또는 pytest 실행 동안 필요한 자원을 제공하는 반복자. 종료 시 정리 작업을 수행한다.
    """
    rows = []
    yield rows
    target = PROJECT_ROOT / ".reports/pytest.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "mode": "fixture",
                "passed": sum(row["outcome"] == "passed" for row in rows),
                "failed": sum(row["outcome"] == "failed" for row in rows),
                "tests": rows,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


@pytest.fixture(autouse=True)
def record(request, results):
    """HTTP가 없는 규칙 테스트도 보고서에서 빠뜨리지 않는다.

    Args:
        request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.
        results: pytest 결과와 HTTP 기록을 모을 목록.

    Returns:
        Iterator: with 또는 pytest 실행 동안 필요한 자원을 제공하는 반복자. 종료 시 정리 작업을 수행한다.
    """
    request.node.exchanges = []
    yield
    call_report = getattr(request.node, "report_call", None)
    report = call_report or getattr(request.node, "report_setup", None)
    results.append(
        {
            "name": request.node.nodeid,
            "outcome": report.outcome if report else "unknown",
            "duration_seconds": call_report.duration if call_report else None,
            "exchanges": request.node.exchanges,
        }
    )


@pytest.fixture(scope="session")
def fixture_settings(tmp_path_factory):
    """GPU 없이 실행할 FastAPI 테스트 설정을 구성한다.

    Args:
        tmp_path_factory: 테스트용 임시 디렉터리를 만드는 pytest 도구.

    Returns:
        Settings: fixture 모드와 임시 저장 경로를 담은 설정.
    """
    return Settings(
        api_key=TOKEN,
        generation_mode="fixture",
        validation_similarity_backend="char_ngram",
        fallback_on_error=False,
        _env_file=None,
        database_path=tmp_path_factory.mktemp("click-detective") / "test.sqlite3",
        diagnostics_path=tmp_path_factory.mktemp("click-traces") / "trace.jsonl",
    )


@pytest.fixture(scope="session")
def client(fixture_settings):
    """HTTP 테스트용 FastAPI 클라이언트를 실행한다.

    Args:
        fixture_settings: GPU 없이 실행할 FastAPI 설정.

    Returns:
        Iterator: 실행 중인 HTTP 테스트 클라이언트.
    """
    with TestClient(create_app(fixture_settings)) as instance:
        yield instance


@pytest.fixture
def api(client, request):
    """실제 응답을 assertion 이전에 기록하는 호출 함수를 제공한다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.
        request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

    Returns:
        실제 응답을 assertion 이전에 기록하는 호출 함수를 제공한다.
    """

    def send(method, path, body=None, game_token=None, authenticated=True, **kwargs):
        """인증과 JSON·미디어 응답을 함께 지원한다.

        Args:
            method: HTTP 요청 메서드. 예: GET, POST.
            path: 저장 파일 경로나 HTTP 요청 경로.
            body: 전송하거나 비교할 JSON 요청 본문.
            game_token: 해당 수사에 접근할 비밀 토큰.
            authenticated: 테스트 요청에 서비스 인증 헤더를 넣을지 여부.
            kwargs: 클라이언트 요청에 전달할 추가 옵션.

        Returns:
            httpx.Response: 테스트 앱의 상태 코드·헤더·본문을 옮긴 HTTP 응답.
        """
        headers = {"Authorization": "Bearer " + TOKEN} if authenticated else {}
        if game_token:
            headers["X-Game-Token"] = game_token
        headers.update(kwargs.pop("headers", {}))
        response = client.request(method, path, json=body, headers=headers, **kwargs)
        try:
            output = response.json()
        except ValueError:
            output = {
                "content_type": response.headers.get("content-type"),
                "bytes": len(response.content),
            }
        request.node.exchanges.append(
            {
                "input": {
                    "method": method,
                    "path": path,
                    "body": redact(body),
                    "headers": redact(headers),
                },
                "output": {"status": response.status_code, "body": redact(output)},
            }
        )
        return response

    return send


@pytest.fixture
def game(api):
    """현재 실제 사건 버전으로 독립 수사를 만든다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.

    Returns:
        dict: 접근 토큰과 사건 버전을 확인한 내부 수사 상태.
    """
    catalog = api("GET", "/v1/catalog").json()
    response = api(
        "POST",
        "/v1/games",
        {
            "request_id": str(uuid4()),
            "case_id": catalog["caseId"],
            "scenario_version": catalog["scenarioVersion"],
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture
def play(api, game):
    """상태 변경의 새 revision을 보관하는 실제 게임 API 실행 도우미.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

    Returns:
        상태 변경의 새 revision을 보관하는 실제 게임 API 실행 도우미.
    """

    return Player(api, game)
