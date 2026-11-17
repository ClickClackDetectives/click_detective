"""investigation/test_game_progress.py의 회귀 동작을 확인한다."""

from uuid import uuid4

from tests.investigation.data_helpers import read


def test_cache_revision_detail_and_notes(api, play):
    """반복 열람·완료 재전송·UUID 충돌·오래된 revision·저장 복원을 검사한다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    base = "/v1/games/" + play.game_id
    body = {"request_id": str(uuid4()), "expected_revision": 0, "evidence_id": "1-01"}
    first = api("POST", base + "/examinations", body, play.token)
    assert first.status_code == 200
    assert api("POST", base + "/examinations", body, play.token).json() == first.json()
    assert (
        api(
            "POST", base + "/examinations", body | {"evidence_id": "1-02"}, play.token
        ).status_code
        == 409
    )
    assert (
        api(
            "PUT",
            base + "/notes",
            {"request_id": str(uuid4()), "expected_revision": 0, "text": "stale"},
            play.token,
        ).status_code
        == 409
    )
    play.state = first.json()["state"]
    before = play.state["revision"]
    play.act("examinations", evidence_id="1-01")
    assert play.state["revision"] == before
    detail = api("GET", base + "/materials/evidence:1-01", game_token=play.token)
    assert detail.json()["body"] == next(
        record["body"]
        for record in read("evidence.json")["records"]
        if record["id"] == "1-01"
    )
    assert (
        api("GET", detail.json()["illustration"], game_token=play.token).status_code
        == 200
    )
    assert (
        api(
            "GET",
            base + "/materials?archive_kind=evidence&search=서재",
            game_token=play.token,
        ).status_code
        == 200
    )
    play.act("notes", text="SQL 입력도 데이터입니다. '); DROP TABLE games; --")
    restored = api("GET", base, game_token=play.token).json()["state"]
    assert restored["notes"] == play.state["notes"]


def test_full_game_to_100_percent_and_correct_verdict(api, play):
    """데이터 29개·쟁점 10개·추론 10개를 실제 획득하고 정확한 고발로 종결한다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
        play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    records, findings, inferences = (
        read("evidence.json")["records"],
        read("findings.private.json")["rules"],
        read("inferences.private.json")["rules"],
    )
    for phase in (1, 2):
        for record in records:
            if record["phase"] == phase:
                play.act("examinations", evidence_id=record["id"])
                if phase == 2:
                    base = f"/v1/games/{play.game_id}"
                    detail = api(
                        "GET",
                        base + "/materials/evidence:" + record["id"],
                        game_token=play.token,
                    ).json()
                    assert detail["illustration"]
                    image = api("GET", detail["illustration"], game_token=play.token)
                    assert image.status_code == 200
                    assert image.headers["content-type"] == "image/png"
                    assert image.content.startswith(b"\x89PNG\r\n\x1a\n")
        for rule in findings:
            if rule["flag"] not in play.state["revealed"] and all(
                key in play.state["examined"] for key in rule["need"]
            ):
                for key in rule["need"]:
                    play.act(
                        "interrogations",
                        suspect_id=rule["suspectId"],
                        question="제시한 자료의 경위를 설명하세요.",
                        material_id=key,
                    )
        if phase == 2:
            for suspect in ("cha", "baek"):
                play.act(
                    "interrogations",
                    suspect_id=suspect,
                    question="그날 밤의 동선을 설명하세요.",
                    topic_id="movement",
                )
        pending = [rule for rule in inferences if rule["phase"] == phase]
        while pending:
            ready = next(
                (
                    rule
                    for rule in pending
                    if all(
                        ref["kind"] != "derived"
                        or ref["id"] in play.state["derivedEvidence"]
                        for ref in rule["sources"]
                    )
                ),
                None,
            )
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
        assert (
            api(
                "GET",
                f"/v1/games/{play.game_id}/materials/{material_key}",
                game_token=play.token,
            ).status_code
            == 200
        )
    solution = read("solution.private.json")["solution"]
    answer = play.act(
        "accusations",
        suspect_id=solution["suspectId"],
        motive=solution["motive"],
        method=solution["method"],
        evidence_ids=list(play.state["derivedEvidence"]),
    )
    assert answer["state"]["verdict"]["score"] == 100
    assert answer["state"]["verdict"]["correct"]
    assert len(answer["state"]["verdict"]["review"]["findings"]) == 10
    denied = api(
        "PUT",
        f"/v1/games/{play.game_id}/notes",
        {
            "request_id": str(uuid4()),
            "expected_revision": play.state["revision"],
            "text": "late",
        },
        play.token,
    )
    assert denied.status_code == 409
