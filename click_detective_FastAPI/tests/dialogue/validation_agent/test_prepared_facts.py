"""전처리에서 준비한 승인 사실을 v2 검증이 사용하는지 검사한다."""

from app.dialogue.interrogation_graph import InterrogationGraph
from app.dialogue.schemas import CharacterReplyRequest
from scripts.live_dialogue.agent_inputs import load_agent_inputs
from tests.dialogue.validation_agent.test_v2 import ScriptedModel


async def test_v2_delivers_prepared_optional_fact_for_paraphrased_question(
    fixture_settings,
):
    """질문에 같은 단어가 없어도 이미 선정된 사실은 문장 검증 뒤 전달한다.

    Args:
        fixture_settings: 실제 모델 생성 없이 그래프를 실행할 서버 설정.

    Returns:
        None: 전처리가 받은 선택 사실과 검증 결과의 ID가 일치해야 한다.
    """
    body = load_agent_inputs(None, 1)[0]
    body.update(question="무슨 용건이죠?", required_fact_ids=[])
    request = CharacterReplyRequest.model_validate(body)
    settings = fixture_settings.model_copy(update={"validation_agent_version": "v2.2"})
    model = ScriptedModel("예약해 둔 책을 받으러 왔어요.")
    result = await InterrogationGraph(settings, model).generate(request)
    assert result.finish_reason == "stop"
    assert result.used_fact_ids == ["visit-reason"]
