# tests/conftest.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../tests/conftest.py)

## 역할과 읽는 순서

모든 테스트는 새 프로젝트 내부 데이터·임시 DB를 사용하고 HTTP 입력·출력을 기록한다.

테스트 파일은 실제 프로젝트 데이터를 사용하되 fixture와 모의 모델을 구분합니다. 테스트 통과는 GPU 품질의 독립 검증이 아닙니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## 모듈 설정과 상수

```python
TOKEN = "click-test-service-secret"
```

이 값은 코드 선언입니다. 실제 .env 비밀값이나 수사 DB 값은 여기에 읽어 넣지 않았습니다.

## redact

[원본 14번째 줄](../../../tests/conftest.py#L14)

인증·게임 토큰은 JSON 보고서에서 숨긴다. 실제 질문·응답은 보존한다.

### 입력과 처리

```python
def redact(value):
```

주요 분기 조건은 `isinstance(value, dict)`, `isinstance(value, list)`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def redact(value):
    """인증·게임 토큰은 JSON 보고서에서 숨긴다. 실제 질문·응답은 보존한다."""
    if isinstance(value, dict):
        return {key: "[REDACTED]" if key.lower() in {"authorization", "x-game-token", "game_token"} else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value
````

## pytest_runtest_makereport

[원본 24번째 줄](../../../tests/conftest.py#L24)

검사 결과를 테스트 종료 후 보고서에서 읽을 수 있게 보관한다.

### 입력과 처리

```python
def pytest_runtest_makereport(item, call):
```

### 실제 코드

````python
def pytest_runtest_makereport(item, call):
    """검사 결과를 테스트 종료 후 보고서에서 읽을 수 있게 보관한다."""
    outcome = yield
    setattr(item, "report_" + call.when, outcome.get_result())
````

## results

[원본 31번째 줄](../../../tests/conftest.py#L31)

모든 검사 결과와 HTTP 왕복을 하나의 JSON에 저장한다.

### 입력과 처리

```python
def results():
```

### 실제 코드

````python
def results():
    """모든 검사 결과와 HTTP 왕복을 하나의 JSON에 저장한다."""
    rows = []
    yield rows
    target = PROJECT_ROOT / ".reports/pytest.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps({"mode": "fixture", "passed": sum(row["outcome"] == "passed" for row in rows),
        "failed": sum(row["outcome"] == "failed" for row in rows), "tests": rows}, ensure_ascii=False, indent=2))
````

## record

[원본 42번째 줄](../../../tests/conftest.py#L42)

HTTP가 없는 규칙 테스트도 보고서에서 빠뜨리지 않는다.

### 입력과 처리

```python
def record(request, results):
```

### 실제 코드

````python
def record(request, results):
    """HTTP가 없는 규칙 테스트도 보고서에서 빠뜨리지 않는다."""
    request.node.exchanges = []
    yield
    report = getattr(request.node, "report_call", None) or getattr(request.node, "report_setup", None)
    results.append({"name": request.node.nodeid, "outcome": report.outcome if report else "unknown",
                    "exchanges": request.node.exchanges})
````

## client

[원본 52번째 줄](../../../tests/conftest.py#L52)

실제 FastAPI를 GPU 없는 명시적 fixture 모드로 실행한다.

### 입력과 처리

```python
def client(tmp_path_factory):
```

### 실제 코드

````python
def client(tmp_path_factory):
    """실제 FastAPI를 GPU 없는 명시적 fixture 모드로 실행한다."""
    config = Settings(api_key=TOKEN, generation_mode="fixture", fallback_on_error=False, _env_file=None,
        database_path=tmp_path_factory.mktemp("click-detective") / "test.sqlite3",
        diagnostics_path=tmp_path_factory.mktemp("click-traces") / "trace.jsonl")
    with TestClient(create_app(config)) as instance:
        yield instance
````

## api

[원본 62번째 줄](../../../tests/conftest.py#L62)

실제 응답을 assertion 이전에 기록하는 호출 함수를 제공한다.

### 입력과 처리

```python
def api(client, request):
```

주요 분기 조건은 `game_token`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
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
````

## game

[원본 82번째 줄](../../../tests/conftest.py#L82)

현재 실제 사건 버전으로 독립 수사를 만든다.

### 입력과 처리

```python
def game(api):
```

### 실제 코드

````python
def game(api):
    """현재 실제 사건 버전으로 독립 수사를 만든다."""
    catalog = api("GET", "/v1/catalog").json()
    response = api("POST", "/v1/games", {"request_id": str(uuid4()), "case_id": catalog["caseId"], "scenario_version": catalog["scenarioVersion"]})
    assert response.status_code == 200, response.text
    return response.json()
````

## play

[원본 91번째 줄](../../../tests/conftest.py#L91)

상태 변경의 새 revision을 보관하는 실제 게임 API 실행 도우미.

### 입력과 처리

```python
def play(api, game):
```

### 실제 코드

````python
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
````

