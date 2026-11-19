"""대화 에이전트 테스트에 필요한 승인 요청을 구성한다."""

from uuid import uuid4

from app.investigation.api.schemas import Interrogate


def profile_request(service):
    """두 문장으로 구성된 실제 인물 소개를 승인 요청으로 만든다.

    Args:
        service: fixture 모드로 초기화한 수사 서비스.

    Returns:
        CharacterReplyRequest: 윤재혁 소개의 두 문장을 필수로 포함하는 요청.
    """
    state = service.engine.initial(str(uuid4()))
    command = Interrogate(
        request_id=uuid4(),
        expected_revision=0,
        suspect_id="yoon",
        question="자기소개를 해주세요.",
    )
    return service.dialogue_request(
        state, command, service.planner.prepare(state, command)
    )
