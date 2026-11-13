# tests/test_runtime.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../tests/test_runtime.py)

## 역할과 읽는 순서

실제 GPU 없이 세 에이전트 연결·실패 무소비·생성 중 상태 충돌을 검사한다.

테스트 파일은 실제 프로젝트 데이터를 사용하되 fixture와 모의 모델을 구분합니다. 테스트 통과는 GPU 품질의 독립 검증이 아닙니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## ApprovedModel

[원본 14번째 줄](../../../tests/test_runtime.py#L14)

승인 원문을 사용해 LangGraph의 생성·검증 호출을 재현하는 모의 모델.

## ApprovedModel.__init__

[원본 19번째 줄](../../../tests/test_runtime.py#L19)

호출 횟수로 생성과 별도 검증이 실제 실행됐는지 확인한다.

### 입력과 처리

```python
def __init__(self):
```

### 실제 코드

````python
def __init__(self):
        """호출 횟수로 생성과 별도 검증이 실제 실행됐는지 확인한다."""
        self.calls = []
````

## ApprovedModel.generate

[원본 23번째 줄](../../../tests/test_runtime.py#L23)

생성은 평문, 검증은 후보 문장 번호를 갖는 엄격한 JSON으로 응답한다.

### 입력과 처리

```python
async def generate(self, messages, *, purpose="dialogue"):
```

async 함수이므로 호출자는 await로 결과를 기다립니다. 대기 중 다른 요청이 실행될 수 있어 revision과 잠금 처리가 필요합니다.

주요 분기 조건은 `'candidate_sentences' not in context`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
async def generate(self, messages, *, purpose="dialogue"):
        """생성은 평문, 검증은 후보 문장 번호를 갖는 엄격한 JSON으로 응답한다."""
        context = json.loads(messages[1]["content"])
        self.calls.append(context)
        if "candidate_sentences" not in context:
            return " ".join(fact["text"] for fact in context["approved_facts"])
        sources = {unit["index"]: unit["text"] for fact in context["approved_facts"] for unit in fact["units"]}
        return json.dumps({"checks": [[unit["index"], True, [part["id"] for part in context["candidate_sentences"]
            if sources[unit["index"]] in part["text"]]] for unit in context["verification_units"]],
            "has_contradiction": False, "has_unsupported_claims": False,
            "history_consistent": True, "persona_consistent": True, "uncertain": False})
````

## test_three_agents_execute_with_backend_approval

[원본 36번째 줄](../../../tests/test_runtime.py#L36)

전처리·생성·검증 노드와 내부 승인 DTO가 실제로 연결되는지 검사한다.

### 입력과 처리

```python
async def test_three_agents_execute_with_backend_approval(client, game):
```

async 함수이므로 호출자는 await로 결과를 기다립니다. 대기 중 다른 요청이 실행될 수 있어 revision과 잠금 처리가 필요합니다.

### 실제 코드

````python
async def test_three_agents_execute_with_backend_approval(client, game):
    """전처리·생성·검증 노드와 내부 승인 DTO가 실제로 연결되는지 검사한다."""
    service = client.app.state.service
    state = service.read(game["game_id"], game["game_token"])
    command = Interrogate(request_id=uuid4(), expected_revision=0, suspect_id="kang", question="자기소개를 해주세요.")
    plan = service.planner.prepare(state, command)
    request = service.dialogue_request(state, command, plan)
    model = ApprovedModel()
    graph = InterrogationGraph(service.settings, model)
    assert {"preprocess_agent", "inference_agent", "validation_agent"} <= set(graph.graph.get_graph().nodes)
    response = await graph.generate(request)
    assert response.finish_reason == "stop"
    assert response.used_fact_ids == [fact.id for fact in request.allowed_facts]
    assert len(model.calls) == 2
    assert service.read(game["game_id"], game["game_token"])["questions"] == 0
````

## test_generation_failure_does_not_consume_state

[원본 53번째 줄](../../../tests/test_runtime.py#L53)

모델 실패가 질문·진술·revision을 변경하지 않으며 같은 요청을 재시도할 수 있다.

### 입력과 처리

```python
def test_generation_failure_does_not_consume_state(api, client, game, monkeypatch):
```

### 실제 코드

````python
def test_generation_failure_does_not_consume_state(api, client, game, monkeypatch):
    """모델 실패가 질문·진술·revision을 변경하지 않으며 같은 요청을 재시도할 수 있다."""
    class FailingGraph:
        """검증 또는 추론 실패를 HTTP 오류로 재현한다."""
        async def generate(self, request):
            """실제 GPU를 사용하지 않는다."""
            raise HTTPException(502, "Generation service failed")

    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service, "graph", FailingGraph())
    path = f"/v1/games/{game['game_id']}"
    body = {"request_id": str(uuid4()), "expected_revision": 0, "suspect_id": "kang", "question": "자기소개를 해주세요."}
    for _ in range(2):
        assert api("POST", path + "/interrogations", body, game["game_token"]).status_code == 502
    restored = api("GET", path, game_token=game["game_token"]).json()["state"]
    assert restored["questions"] == 0
    assert restored["revision"] == 0
    assert restored["messages"] == []
````

## test_state_change_during_generation_rejects_stale_reply

[원본 74번째 줄](../../../tests/test_runtime.py#L74)

생성 중 다른 행동이 확정되면 오래된 대사를 저장하지 않는다.

### 입력과 처리

```python
async def test_state_change_during_generation_rejects_stale_reply(client, game, monkeypatch):
```

async 함수이므로 호출자는 await로 결과를 기다립니다. 대기 중 다른 요청이 실행될 수 있어 revision과 잠금 처리가 필요합니다.

### 실제 코드

````python
async def test_state_change_during_generation_rejects_stale_reply(client, game, monkeypatch):
    """생성 중 다른 행동이 확정되면 오래된 대사를 저장하지 않는다."""
    started, release = asyncio.Event(), asyncio.Event()

    class WaitingGraph:
        """모델 대기 동안 다른 API의 상태 변경이 가능한 상황을 재현한다."""
        async def generate(self, request):
            """승인 원문을 응답하더라도 revision이 달라지면 저장 단계에서 거절돼야 한다."""
            started.set()
            await release.wait()
            return CharacterReplyResponse(request_id=request.request_id, suspect_id=request.suspect_id,
                state_revision=request.state_revision, reply=" ".join(fact.text for fact in request.allowed_facts),
                used_fact_ids=request.required_fact_ids, model_version="waiting-contract", finish_reason="stop")

    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service, "graph", WaitingGraph())
    command = Interrogate(request_id=uuid4(), expected_revision=0, suspect_id="kang", question="자기소개를 해주세요.")
    task = asyncio.create_task(service.change(game["game_id"], game["game_token"], command, "interrogate"))
    try:
        await asyncio.wait_for(started.wait(), timeout=2)
        with pytest.raises(HTTPException) as duplicate:
            await service.change(game["game_id"], game["game_token"], command, "interrogate")
        assert duplicate.value.status_code == 409
        await service.change(game["game_id"], game["game_token"], Notes(request_id=uuid4(), expected_revision=0, text="생성 중 저장"), "notes")
    finally:
        release.set()
    with pytest.raises(HTTPException) as stale:
        await task
    assert stale.value.status_code == 409
    state = service.read(game["game_id"], game["game_token"])
    assert state["notes"] == "생성 중 저장"
    assert state["revision"] == 1 and state["questions"] == 0
````

## test_all_business_routes_have_coverage

[원본 109번째 줄](../../../tests/test_runtime.py#L109)

새 API가 생기면 검사 목록을 함께 갱신하도록 OpenAPI 경로를 확인한다.

### 입력과 처리

```python
def test_all_business_routes_have_coverage(api):
```

### 실제 코드

````python
def test_all_business_routes_have_coverage(api):
    """새 API가 생기면 검사 목록을 함께 갱신하도록 OpenAPI 경로를 확인한다."""
    response = api("GET", "/openapi.json", authenticated=False)
    assert response.status_code == 200
    actual = {(method.upper(), path) for path, methods in response.json()["paths"].items()
              for method in methods if method in {"get", "post", "put", "patch", "delete"}}
    expected = {
        ("GET", "/healthz"), ("GET", "/v1/catalog"), ("GET", "/v1/cases"), ("GET", "/v1/cases/{case_id}"),
        ("GET", "/v1/assets/{asset_path}"), ("POST", "/v1/games"), ("GET", "/v1/games/{game_id}"),
        ("GET", "/v1/games/{game_id}/materials"), ("GET", "/v1/games/{game_id}/materials/{material_key}"),
        ("GET", "/v1/games/{game_id}/evidence-assets/{evidence_id}"), ("GET", "/v1/games/{game_id}/findings"),
        ("GET", "/v1/games/{game_id}/views/{screen}"),
        ("POST", "/v1/games/{game_id}/examinations"), ("POST", "/v1/games/{game_id}/interrogations"),
        ("POST", "/v1/games/{game_id}/inferences"), ("POST", "/v1/games/{game_id}/phase-transitions"),
        ("PUT", "/v1/games/{game_id}/notes"), ("POST", "/v1/games/{game_id}/accusations"),
    }
    assert actual == expected
````

