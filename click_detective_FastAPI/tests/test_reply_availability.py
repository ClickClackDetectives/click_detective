"""게임에서 전송한 유효 질문은 모델 실패·쟁점 여부와 무관하게 답변을 확정한다."""

from uuid import uuid4
import pytest
from fastapi import HTTPException

from app.config import Settings
from app.dialogue.interrogation_graph import InterrogationGraph


@pytest.mark.parametrize('failure', [
    HTTPException(502, 'Generation service failed'),
    HTTPException(504, 'Generation timed out'),
    HTTPException(422, 'Approved context exceeds local token budget'),
    RuntimeError('model runtime failed'),
    ValueError('invalid generated output'),
])
def test_valid_question_always_gets_approved_reply(api, client, game, monkeypatch, failure):
    """모델 실패는 200 fallback으로 복구하며 같은 UUID를 중복 소비하지 않는다."""
    class FailingGraph:
        """모델 경로의 실패만 주입하고 승인·저장 로직은 실제 코드를 사용한다."""
        calls = 0

        async def generate(self, request):
            self.calls += 1
            raise failure

    graph = FailingGraph()
    service = client.app.state.service
    monkeypatch.setattr(service.settings, 'generation_mode', 'local')
    monkeypatch.setattr(service.settings, 'fallback_on_error', True)
    monkeypatch.setattr(service, 'graph', graph)
    path = '/v1/games/' + game['game_id'] + '/interrogations'
    body = {'request_id': str(uuid4()), 'expected_revision': 0, 'suspect_id': 'kang',
            'question': '자기소개를 해주세요.'}
    response = api('POST', path, body, game['game_token'])
    assert response.status_code == 200
    payload = response.json()
    assert payload['result']['finish_reason'] == 'fallback'
    assert payload['result']['reply'] == service.c.people['kang']['statement']
    assert payload['result']['used_fact_ids'] == ['kang-profile']
    assert payload['state']['questions'] == 1
    assert payload['state']['revision'] == 1
    assert len(payload['state']['messages']) == 2
    assert payload['state']['findingDetails'] == []
    assert api('POST', path, body, game['game_token']).json() == payload
    assert graph.calls == 1


def test_failed_generated_admission_still_commits_only_approved_finding(api, client, play, monkeypatch):
    """복구 대사는 실제 획득·제시 조건을 통과한 쟁점만 기록한다."""
    class FailingGraph:
        async def generate(self, request):
            raise RuntimeError('inference unavailable')

    service = client.app.state.service
    monkeypatch.setattr(service.settings, 'generation_mode', 'local')
    monkeypatch.setattr(service.settings, 'fallback_on_error', True)
    monkeypatch.setattr(service, 'graph', FailingGraph())
    play.act('examinations', evidence_id='S-Y')
    response = play.act('interrogations', suspect_id='yoon', question='장부의 경위를 설명하세요.', material_id='S-Y')
    assert response['result']['finish_reason'] == 'fallback'
    assert response['state']['revealed'] == ['yoon_money']
    assert '12억' in response['result']['reply']
    assert response['state']['questions'] == 1
    assert len(response['state']['findingDetails']) == 1


async def test_real_graph_rejection_recovers_approved_fact(client, monkeypatch):
    """3노드 그래프가 출력 형식을 거절해도 원문 복구가 이루어진다."""
    class InvalidModel:
        model_version = 'invalid-output-test'

        async def generate(self, messages, *, purpose="dialogue"):
            return '{invalid output'

    from app.schemas import Interrogate
    service = client.app.state.service
    monkeypatch.setattr(service.settings, 'fallback_on_error', True)
    state = service.engine.initial(str(uuid4()))
    command = Interrogate(request_id=uuid4(), expected_revision=0, suspect_id='kang', question='자기소개를 해주세요.')
    request = service.dialogue_request(state, command, service.planner.prepare(state, command))
    response = await InterrogationGraph(service.settings, InvalidModel()).generate(request)
    assert response.finish_reason == 'fallback'
    assert response.reply == service.c.people['kang']['statement']


def test_default_player_policy_enables_reply_recovery():
    """신규 실행도 기본적으로 생성 오류를 플레이어에게 502로 내보내지 않는다."""
    config = Settings(api_key='test-api-secret-long-enough', _env_file=None)
    assert config.fallback_on_error is True
