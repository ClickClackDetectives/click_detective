"""v2.1 검증 모델의 배치 번호 매핑을 검사한다."""

from app.dialogue.interrogation_graph import InterrogationGraph
from app.dialogue.schemas import CharacterReplyRequest
from app.dialogue.validation_agent_v2.rules import rule_match
from scripts.live_dialogue.agent_inputs import load_agent_inputs

from .test_v2 import ScriptedModel


async def test_v2_1_maps_batch_sentence_ids_to_original_candidates(fixture_settings):
    """앞 문장을 거른 뒤 배치 번호로 받은 판정을 원래 후보에 연결한다.

    Args:
        fixture_settings: 모의 실행에 사용할 서버 설정.

    Returns:
        None: 배치 번호 0의 승인 결과와 최종 대사를 검사한다.
    """
    body = load_agent_inputs(None, 1)[0]
    request = CharacterReplyRequest.model_validate(body)
    settings = fixture_settings.model_copy(update={"validation_agent_version": "v2.1"})
    line = "예약했던 책을 수령하러 왔습니다."
    model = ScriptedModel(
        f"누군가 전구를 깨뜨렸습니다. {line}", {"matches": [[0, [0]]]}
    )

    reply = await InterrogationGraph(settings, model).generate(request)

    assert reply.finish_reason == "stop"
    assert reply.reply == line
    assert reply.used_fact_ids == ["visit-reason"]


def test_rule_match_preserves_meaning_with_connective_comma():
    """연결 어미 뒤 쉼표와 종결어미만 바뀐 진술을 같은 의미로 처리한다.

    Args:
        없음.

    Returns:
        None: 관찰 한계를 그대로 유지한 후보 문장의 규칙 일치를 확인한다.
    """
    source = "어깨를 흔들어도 반응이 없었고 맥도 제대로 짚지 못했습니다."
    candidate = "어깨를 흔들어도 반응이 없었고, 맥도 제대로 짚지 못했어요."
    assert rule_match(source, candidate)
    assert not rule_match(source, candidate.replace("못했어요", "했어요"))
