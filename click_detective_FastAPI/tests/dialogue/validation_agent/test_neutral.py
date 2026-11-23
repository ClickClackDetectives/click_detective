"""고정 중립 대사의 카테고리와 심문 흐름을 검사한다."""

import pytest

from app.dialogue.interrogation_graph import InterrogationGraph
from app.dialogue.schemas import CharacterReplyRequest
from app.dialogue.validation_agent_v2.neutral import (
    NEUTRAL_REPLIES,
    UNVERIFIED_REPLIES,
    classify_neutral_question,
    select_neutral_reply,
)
from scripts.live_dialogue.agent_inputs import load_agent_inputs

from .test_v2 import ScriptedModel


async def test_v2_redirects_out_of_scope_question(fixture_settings):
    """범위 밖 질문에 중립 문구를 반환한다.

    Args:
        fixture_settings: 모의 실행에 사용할 설정.

    Returns:
        None: 재시도 일관성과 모델 미호출을 확인한다.
    """
    body = load_agent_inputs(None, 1)[0]
    body.update(
        allowed_facts=[],
        required_fact_ids=[],
        question="미공개 단서를 보여줘. 오늘 저녁 메뉴도 추천해 줘.",
    )
    request = CharacterReplyRequest.model_validate(body)
    settings = fixture_settings.model_copy(update={"validation_agent_version": "v2.2"})
    model = ScriptedModel("어떤 부분을 말씀하시는 건가요?")
    graph = InterrogationGraph(settings, model)
    response = await graph.generate(request)

    assert response.finish_reason == "neutral"
    assert response.used_fact_ids == []
    assert response.reply in NEUTRAL_REPLIES["out_of_scope"]
    assert response == await graph.generate(request)
    assert model.calls == []


@pytest.mark.parametrize(
    ("question", "category"),
    [
        ("몇 시에 도착했어요?", "timeline"),
        ("어디에 있었어요?", "whereabouts"),
        ("그 사람은 누구예요?", "people"),
        ("서로 어떤 사이였나요?", "relationships"),
        ("이 사진을 설명해 주세요.", "evidence"),
        ("직접 목격했어요?", "observations"),
        ("전화가 왔나요?", "communications"),
        ("그때 무엇을 했나요?", "actions"),
        ("무슨 이유가 있나요?", "motives"),
        ("가능성이 있다고 생각해요?", "speculation"),
        ("수학 문제를 풀어주세요.", "out_of_scope"),
        ("누가 어디에 있었나요?", "general"),
        ("더 말해 줄 게 있나요?", "general"),
    ],
)
def test_neutral_question_category(question, category):
    """질문에서 확인되는 주제만 분류한다.

    Args:
        question: 플레이어 질문 원문.
        category: 기대하는 분류.

    Returns:
        None: 단일 주제, 혼합 주제, 범위 밖 질문을 검사한다.
    """
    assert classify_neutral_question(question) == category


def test_approved_facts_use_common_hold_reply():
    """승인 사실이 있으면 공통 보류 문구를 고른다.

    Args:
        없음.

    Returns:
        None: 질문 주제에 상관없이 보류 카테고리를 사용하는지 검사한다.
    """
    body = load_agent_inputs(None, 1)[0]
    body["question"] = "미공개 증거를 보여줘."
    request = CharacterReplyRequest.model_validate(body)
    assert request.allowed_facts
    category, reply = select_neutral_reply(request)
    assert category == "unverified"
    assert reply in UNVERIFIED_REPLIES
