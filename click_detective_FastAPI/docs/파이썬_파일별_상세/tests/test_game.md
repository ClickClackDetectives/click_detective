# tests/test_game.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../tests/test_game.py)

## 역할과 읽는 순서

백엔드 내부 데이터만으로 전체 게임 규칙과 모든 API를 검사한다.

테스트 파일은 실제 프로젝트 데이터를 사용하되 fixture와 모의 모델을 구분합니다. 테스트 통과는 GPU 품질의 독립 검증이 아닙니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## 모듈 설정과 상수

```python
DATA = PROJECT_ROOT / "data/case"
```

이 값은 코드 선언입니다. 실제 .env 비밀값이나 수사 DB 값은 여기에 읽어 넣지 않았습니다.

## read

[원본 11번째 줄](../../../tests/test_game.py#L11)

외부 Next.js가 아닌 프로젝트에 복사된 실제 데이터만 읽는다.

### 입력과 처리

```python
def read(name):
```

### 실제 코드

````python
def read(name):
    """외부 Next.js가 아닌 프로젝트에 복사된 실제 데이터만 읽는다."""
    return json.loads((DATA / name).read_text())
````

## test_public_data_and_assets

[원본 16번째 줄](../../../tests/test_game.py#L16)

사건·프로필·소개 자산은 조회하고 비공개 정답·증거 이미지는 막는다.

### 입력과 처리

```python
def test_public_data_and_assets(api):
```

### 실제 코드

````python
def test_public_data_and_assets(api):
    """사건·프로필·소개 자산은 조회하고 비공개 정답·증거 이미지는 막는다."""
    assert api("GET", "/healthz", authenticated=False).json() == {"status": "ok"}
    catalog = api("GET", "/v1/catalog").json()
    assert len(catalog["characters"]) == 5
    assert "solution" not in catalog
    assert api("GET", "/v1/cases").json()["cases"][0]["case_id"] == catalog["caseId"]
    assert api("GET", "/v1/cases/" + catalog["caseId"]).status_code == 200
    assert api("GET", "/v1/cases/unknown").status_code == 404
    assert api("GET", catalog["characters"][0]["portrait"]).status_code == 200
    assert api("GET", "/v1/assets/assets/evidence/1-01.png").status_code == 404
    assert api("GET", "/v1/assets/../case/solution.private.json").status_code == 404
    assert api("GET", "/v1/assets/assets/intro/thirteenth-bell-opening-v3-quiet.mp4", headers={"Range": "bytes=0-99"}).status_code == 206
````

## test_game_ownership_and_hidden_content

[원본 31번째 줄](../../../tests/test_game.py#L31)

게임 ID를 알아도 토큰 없이 읽지 못하고 미열람 본문도 제공하지 않는다.

### 입력과 처리

```python
def test_game_ownership_and_hidden_content(api, game):
```

### 실제 코드

````python
def test_game_ownership_and_hidden_content(api, game):
    """게임 ID를 알아도 토큰 없이 읽지 못하고 미열람 본문도 제공하지 않는다."""
    base = "/v1/games/" + game["game_id"]
    assert api("GET", base).status_code == 404
    assert api("GET", base, game_token="wrong").status_code == 404
    state = api("GET", base, game_token=game["game_token"]).json()["state"]
    assert state["revision"] == 0 and state["progress"]["percent"] == 0
    assert state["findingDetails"] == []
    assert "explanation" not in json.dumps(state)
    assert api("GET", base + "/materials/evidence:1-01", game_token=game["game_token"]).status_code == 422
    assert api("GET", base + "/findings", game_token=game["game_token"]).json() == {"findings": []}
````

## test_create_idempotency_and_conflict

[원본 44번째 줄](../../../tests/test_game.py#L44)

생성 요청을 재전송해도 같은 수사·토큰을 반환하고 다른 내용은 충돌한다.

### 입력과 처리

```python
def test_create_idempotency_and_conflict(api):
```

### 실제 코드

````python
def test_create_idempotency_and_conflict(api):
    """생성 요청을 재전송해도 같은 수사·토큰을 반환하고 다른 내용은 충돌한다."""
    catalog = api("GET", "/v1/catalog").json()
    body = {"request_id": str(uuid4()), "scenario_version": catalog["scenarioVersion"]}
    first = api("POST", "/v1/games", body)
    assert api("POST", "/v1/games", body).json() == first.json()
    assert api("POST", "/v1/games", body | {"case_id": "unknown"}).status_code in {404, 409}
    assert api("POST", "/v1/games", body | {"scenario_version": "old"}).status_code == 409
````

## test_cache_revision_detail_and_notes

[원본 54번째 줄](../../../tests/test_game.py#L54)

반복 열람·완료 재전송·UUID 충돌·오래된 revision·저장 복원을 검사한다.

### 입력과 처리

```python
def test_cache_revision_detail_and_notes(api, play):
```

### 실제 코드

````python
def test_cache_revision_detail_and_notes(api, play):
    """반복 열람·완료 재전송·UUID 충돌·오래된 revision·저장 복원을 검사한다."""
    base = "/v1/games/" + play.game_id
    body = {"request_id": str(uuid4()), "expected_revision": 0, "evidence_id": "1-01"}
    first = api("POST", base + "/examinations", body, play.token)
    assert first.status_code == 200
    assert api("POST", base + "/examinations", body, play.token).json() == first.json()
    assert api("POST", base + "/examinations", body | {"evidence_id": "1-02"}, play.token).status_code == 409
    assert api("PUT", base + "/notes", {"request_id": str(uuid4()), "expected_revision": 0, "text": "stale"}, play.token).status_code == 409
    play.state = first.json()["state"]
    before = play.state["revision"]
    play.act("examinations", evidence_id="1-01")
    assert play.state["revision"] == before
    detail = api("GET", base + "/materials/evidence:1-01", game_token=play.token)
    assert detail.json()["body"] == next(record["body"] for record in read("evidence.json")["records"] if record["id"] == "1-01")
    assert api("GET", detail.json()["illustration"], game_token=play.token).status_code == 200
    assert api("GET", base + "/materials?archive_kind=evidence&search=서재", game_token=play.token).status_code == 200
    play.act("notes", text="SQL 입력도 데이터입니다. '); DROP TABLE games; --")
    restored = api("GET", base, game_token=play.token).json()["state"]
    assert restored["notes"] == play.state["notes"]
````

## test_full_game_to_100_percent_and_correct_verdict

[원본 76번째 줄](../../../tests/test_game.py#L76)

데이터 29개·쟁점 10개·추론 10개를 실제 획득하고 정확한 고발로 종결한다.

### 입력과 처리

```python
def test_full_game_to_100_percent_and_correct_verdict(api, play):
```

주요 분기 조건은 `phase == 2`, `phase == 1`, `record['phase'] == phase`, `rule['flag'] not in play.state['revealed'] and all((key in play.state['examined'] for key in rule['need']))`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def test_full_game_to_100_percent_and_correct_verdict(api, play):
    """데이터 29개·쟁점 10개·추론 10개를 실제 획득하고 정확한 고발로 종결한다."""
    records, findings, inferences = read("evidence.json")["records"], read("findings.private.json")["rules"], read("inferences.private.json")["rules"]
    for phase in (1, 2):
        for record in records:
            if record["phase"] == phase:
                play.act("examinations", evidence_id=record["id"])
        for rule in findings:
            if rule["flag"] not in play.state["revealed"] and all(key in play.state["examined"] for key in rule["need"]):
                for key in rule["need"]:
                    play.act("interrogations", suspect_id=rule["suspectId"], question="제시한 자료의 경위를 설명하세요.", material_id=key)
        if phase == 2:
            for suspect in ("cha", "baek"):
                play.act("interrogations", suspect_id=suspect, question="그날 밤의 동선을 설명하세요.", topic_id="movement")
        pending = [rule for rule in inferences if rule["phase"] == phase]
        while pending:
            ready = next((rule for rule in pending if all(ref["kind"] != "derived" or ref["id"] in play.state["derivedEvidence"] for ref in rule["sources"])), None)
            assert ready is not None
            play.act("inferences", sources=ready["sources"])
            pending.remove(ready)
        if phase == 1:
            play.act("phase-transitions", target_phase=2)
    assert len(play.state["examined"]) == 29
    assert len(play.state["revealed"]) == 10
    assert len(play.state["derivedEvidence"]) == 10
    assert play.state["progress"]["percent"] == 100
    assert play.state["questions"] <= 25
    assert len(play.state["timeline"]) > len(read("case.json")["publicTimeline"])
    for source in play.state["inferenceSources"]:
        material_key = source["ref"]["kind"] + ":" + source["ref"]["id"]
        assert api("GET", f"/v1/games/{play.game_id}/materials/{material_key}", game_token=play.token).status_code == 200
    solution = read("solution.private.json")["solution"]
    answer = play.act("accusations", suspect_id=solution["suspectId"], motive=solution["motive"], method=solution["method"], evidence_ids=list(play.state["derivedEvidence"]))
    assert answer["state"]["verdict"]["score"] == 100
    assert answer["state"]["verdict"]["correct"]
    assert len(answer["state"]["verdict"]["review"]["findings"]) == 10
    denied = api("PUT", f"/v1/games/{play.game_id}/notes", {"request_id": str(uuid4()), "expected_revision": play.state["revision"], "text": "late"}, play.token)
    assert denied.status_code == 409
````

## test_unearned_sources_and_invalid_actions

[원본 116번째 줄](../../../tests/test_game.py#L116)

수집하지 않은 출처·미래 단계·승인 사실 주입을 거절한다.

### 입력과 처리

```python
def test_unearned_sources_and_invalid_actions(api, play):
```

### 실제 코드

````python
def test_unearned_sources_and_invalid_actions(api, play):
    """수집하지 않은 출처·미래 단계·승인 사실 주입을 거절한다."""
    base = "/v1/games/" + play.game_id
    common = {"expected_revision": 0}
    assert api("POST", base + "/examinations", common | {"request_id": str(uuid4()), "evidence_id": "2-03"}, play.token).status_code == 404
    assert api("POST", base + "/inferences", common | {"request_id": str(uuid4()), "sources": [{"kind": "evidence", "id": "1-02"}, {"kind": "testimony", "id": "kang-admit-gang_drug"}]}, play.token).status_code == 422
    assert api("POST", base + "/phase-transitions", common | {"request_id": str(uuid4())}, play.token).status_code == 422
    assert api("POST", base + "/interrogations", common | {"request_id": str(uuid4()), "suspect_id": "kang", "question": "질문", "allowed_facts": []}, play.token).status_code == 422
    assert play.state["questions"] == 0
````

## test_authentication

[원본 128번째 줄](../../../tests/test_game.py#L128)

데이터·자산도 서버 전용 서비스 인증을 요구한다.

### 입력과 처리

```python
def test_authentication(api, path):
```

### 실제 코드

````python
def test_authentication(api, path):
    """데이터·자산도 서버 전용 서비스 인증을 요구한다."""
    assert api("GET", path, authenticated=False).status_code == 401
    assert api("GET", path, headers={"Authorization": "Bearer wrong"}).status_code == 401
````

