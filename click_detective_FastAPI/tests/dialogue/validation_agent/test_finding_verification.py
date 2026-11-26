"""강민호의 재방문 쟁점과 검증된 증언의 저장 조건을 검사한다."""

import pytest

from app.dialogue.services.reply.dialogue_interrogation_graph import InterrogationGraph
from tests.investigation.test_minimum_success_route import prepare_shared_case

from .test_v2 import ScriptedModel


@pytest.mark.parametrize(
    ("line", "discovered"),
    [
        ("차용증 원본을 가지러 서재에 갔습니다.", True),
        ("11시 2분에 원본을 복도 꽃병에 숨겼습니다.", True),
        ("어두워서 상태를 확신하지 못했습니다.", False),
        ("어깨를 흔들어도 반응이 없었고 맥도 제대로 짚지 못했습니다.", False),
        ("11시 3분에 원본을 복도 꽃병에 숨겼습니다.", False),
    ],
)
def test_revisit_requires_a_verified_return_or_concealment(
    client, play, monkeypatch, line, discovered
):
    """두 핵심 근거 중 하나가 확인되면 실제 검증된 문장만 저장한다.

    Args:
        client: 심문 서비스를 실행하는 테스트 앱.
        play: 증거 열람과 심문을 실행하는 도우미.
        monkeypatch: 테스트에 사용할 모델로 교체하는 도구.
        line: 모델이 반환할 후보 대사.
        discovered: 쟁점이 저장될 것으로 기대하는지 여부.

    Returns:
        None: 응답과 쟁점 및 증언 저장 여부를 검사한다.
    """
    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(
        service.reply_service,
        "graph",
        InterrogationGraph(service.settings, ScriptedModel(line)),
    )
    play.act("examinations", evidence_id="1-13")
    result = play.act(
        "interrogations",
        suspect_id="kang",
        question="차용증 원본을 찾으러 서재에 다시 간 일을 말씀해 주세요.",
        material_id="1-13",
    )
    state = result["state"]
    fact_id = "kang-admit-gang_visit"
    assert ("gang_visit" in state["revealed"]) == discovered
    if discovered:
        assert result["result"]["used_fact_ids"] == [fact_id]
        assert state["statements"][fact_id]["excerpt"] == line
    else:
        assert result["result"]["finish_reason"] == "neutral"
        assert fact_id not in state["statements"]


@pytest.mark.parametrize(
    ("person", "materials", "flag", "line"),
    [
        (
            "kang",
            ("1-08", "1-02"),
            "gang_drug",
            "제가 와인잔에 수면제 두 알을 넣었습니다.",
        ),
        (
            "baek",
            ("S-B", "1-07"),
            "sera_draft",
            "윤재혁 씨 방 가방에서 초안을 가져왔어요.",
        ),
        ("cha", ("S-C", "1-11"), "cha_identity", "제가 회장님의 친아들입니다."),
        ("yoon", ("S-Y",), "yoon_money", "3년 동안 회사 돈 12억 원을 빼돌렸습니다."),
        ("yoon", ("S-Y", "2-01"), "yoon_visit", "금고에서 장부를 가져왔습니다."),
        (
            "seo",
            ("1-10", "2-02"),
            "seo_forgery",
            "세 점을 위작으로 바꾸고 진품을 팔아 빚을 갚았습니다.",
        ),
        (
            "seo",
            ("2-04", "2-07", "2-11"),
            "seo_burn",
            "벽난로에서 오른쪽 장갑과 일기 한 페이지를 태웠습니다.",
        ),
        (
            "seo",
            ("1-03", "2-03"),
            "weapon_fit",
            "부엉이상 받침과 검시 손상이 부합한다는 지적은 알겠습니다.",
        ),
        (
            "cha",
            ("2-04", "2-11"),
            "witness_gap",
            "뒷모습뿐이라 신원과 태운 물건을 확인하지 못했습니다.",
        ),
    ],
)
def test_core_sentence_unlocks_other_findings(
    client, play, monkeypatch, person, materials, flag, line
):
    """다른 쟁점도 핵심 문장만 확인해 해당 발췌를 저장한다.

    Args:
        client: 심문 서비스를 실행하는 테스트 앱.
        play: 증거 열람과 심문을 실행하는 도우미.
        monkeypatch: 테스트에 사용할 모델로 교체하는 도구.
        person: 심문할 인물의 ID.
        materials: 해당 인물에게 제시할 자료 ID 목록.
        flag: 발견할 쟁점의 ID.
        line: 모델이 반환할 핵심 문장.

    Returns:
        None: 서버 상태의 쟁점과 증언을 검사한다.
    """
    if any(material.startswith("2-") for material in materials):
        prepare_shared_case(play)
    for material in materials:
        if material not in play.state["examined"]:
            play.act("examinations", evidence_id=material)
    for material in materials[:-1]:
        play.act(
            "interrogations",
            suspect_id=person,
            question="이 자료를 설명해 주세요.",
            material_id=material,
        )
    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(
        service.reply_service,
        "graph",
        InterrogationGraph(service.settings, ScriptedModel(line)),
    )
    result = play.act(
        "interrogations",
        suspect_id=person,
        question="이 자료에서 확인한 사실을 설명해 주세요.",
        material_id=materials[-1],
    )
    assert flag in result["state"]["revealed"]
    entry_id = f"{person}-admit-{flag}"
    if flag in {"weapon_fit", "witness_gap"}:
        assert result["result"]["used_fact_ids"] == [f"{person}-finding-{flag}"]
    else:
        assert result["state"]["statements"][entry_id]["excerpt"] == line
