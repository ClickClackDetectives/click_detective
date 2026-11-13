"""원본 Next.js 화면용 조회 계약이 비공개 본문을 유출하지 않고 같은 분류를 제공하는지 검사한다."""
from uuid import uuid4


def test_original_ui_catalog_and_views(api, game):
    """공개 카탈로그·집사 분류·서버 검색·집계·권한·본문 읽기 순서를 확인한다."""
    catalog = api("GET", "/v1/catalog").json()
    assert len(catalog["display"]["evidence"]) == 29
    assert all(record["body"] == "" for record in catalog["display"]["evidence"])
    assert len(catalog["application"]["cases"]) == 4
    assert catalog["display"]["accusationMinimum"] == 0
    base, token = "/v1/games/" + game["game_id"], game["game_token"]
    assert api("GET", base + "/views/evidence").status_code == 404
    state = api("GET", base, game_token=token).json()["state"]
    assert state["ui"]["requiredInferenceIds"] == []
    assert state["ui"]["physicalReadCount"] == 0
    view = api("GET", base + "/views/evidence", game_token=token).json()
    assert len(view["available"]) == 17 and view["readCount"] == 0
    assert all(row["id"] != "1-05" for row in view["available"])
    filtered = api("GET", base + "/views/evidence?place=서재&search=와인", game_token=token).json()
    assert [row["id"] for group in filtered["groups"] for row in group["records"]] == ["1-02"]
    witnesses = api("GET", base + "/views/testimonies", game_token=token).json()["visible"]
    assert [person["id"] for person in witnesses] == ["butler", "yoon", "baek", "kang", "cha", "seo"]
    assert witnesses[0]["records"][0]["id"] == "1-05"
    assert "body" not in witnesses[0]["records"][0]
    assert api("GET", base + "/views/inference", game_token=token).json() == {"visible": []}
    assert api("GET", base + "/views/unknown", game_token=token).status_code == 404
    updated = api("POST", base + "/examinations", {"request_id": str(uuid4()), "expected_revision": 0, "evidence_id": "1-02"}, token).json()["state"]
    assert updated["ui"]["physicalReadCount"] == 1
    sources = api("GET", base + "/views/inference?search=와인", game_token=token).json()["visible"]
    assert sources[0]["ref"] == {"kind": "evidence", "id": "1-02"}
    response = api("POST", base + "/interrogations", {"request_id": str(uuid4()),
        "expected_revision": updated["revision"], "suspect_id": "kang",
        "question": "그날 밤의 동선을 설명하세요.", "topic_id": "movement"}, token)
    assert response.status_code == 200
    history = api("GET", base + "/views/testimonies?person=kang", game_token=token)
    assert history.status_code == 200
    assert len(history.json()["visible"][0]["pairs"]) == 1
