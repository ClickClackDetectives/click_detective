"""전처리에서 준비한 승인 사실을 검증이 사용하는지 검사한다."""

from app.dialogue.dto.dialogue_reply_dto import CharacterReplyRequest
from app.dialogue.services.reply.dialogue_interrogation_graph import InterrogationGraph
from scripts.live_dialogue.agent_inputs import load_agent_inputs
from tests.dialogue.validation_agent.test_v2 import ScriptedModel


async def test_delivers_prepared_optional_fact_for_relevant_question(
    fixture_settings,
):
    """질문과 관련된 선택 사실은 필수 사실이 없어도 검증 뒤 전달한다.

    Args:
        fixture_settings: 실제 모델 생성 없이 그래프를 실행할 서버 설정.

    Returns:
        None: 전처리가 받은 선택 사실과 검증 결과의 ID가 일치해야 한다.
    """
    body = load_agent_inputs(None, 1)[0]
    body.update(question="예약한 책을 받으러 왔나요?", required_fact_ids=[])
    request = CharacterReplyRequest.model_validate(body)
    settings = fixture_settings
    model = ScriptedModel("예약해 둔 책을 받으러 왔어요.")
    result = await InterrogationGraph(settings, model).generate(request)
    assert result.finish_reason == "stop"
    assert result.used_fact_ids == ["visit-reason"]
