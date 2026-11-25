"""실제 사건 승인 데이터로 재서술 허용·호출별 디코딩·사실 변조 거절을 검사한다.

모의 검증 판정은 그래프 계약을 확인하기 위한 것이며 실제 Qwen 품질 측정은 아니다.
"""

import json
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.config import Settings
from app.dialogue.interrogation_graph import InterrogationGraph
from app.dialogue.local_model import decoding_options
from app.dialogue.preprocess_agent.prompt import build_messages
from app.dialogue.validation_agent_v1.critical_facts import critical_claim_error
from app.dialogue.validation_agent_v1.prompt import build_verification_messages
from app.investigation.api.schemas import Interrogate


def make_request(client):
    """프로젝트의 윤재혁 소개 원문을 실제 승인 계획으로 가져온다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.

    Returns:
        CharacterReplyRequest: 현재 사건의 승인 계획으로 구성한 테스트 요청.
    """
    service = client.app.state.service
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


def test_generation_samples_but_verification_does_not():
    """동일 모델이어도 생성 자유도가 검증 JSON 호출에 전달되지 않아야 한다.

    Args:
        없음.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    settings = Settings(
        api_key="test-long-enough-secret",
        _env_file=None,
        dialogue_temperature=0.75,
        dialogue_top_p=0.92,
        dialogue_repetition_penalty=1.08,
    )
    assert decoding_options(settings, "dialogue") == {
        "do_sample": True,
        "temperature": 0.75,
        "top_p": 0.92,
        "repetition_penalty": 1.08,
    }
    assert decoding_options(settings, "verification") == {"do_sample": False}
    settings.dialogue_temperature = 0
    assert decoding_options(settings, "dialogue") == {"do_sample": False}
    with pytest.raises(ValueError):
        decoding_options(settings, "unknown")


@pytest.mark.parametrize(
    "field,value",
    [
        ("dialogue_temperature", -0.1),
        ("dialogue_temperature", float("nan")),
        ("dialogue_top_p", 0),
        ("dialogue_top_p", 1.1),
        ("dialogue_repetition_penalty", 0.9),
    ],
)
def test_sampling_settings_reject_invalid_values(field, value):
    """잘못된 설정을 GPU 실행 전에 거절한다.

    Args:
        field: 검사할 설정 필드 이름.
        value: 검사·변환하거나 비밀값을 가릴 입력 값.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    with pytest.raises(ValidationError):
        Settings(api_key="test-long-enough-secret", _env_file=None, **{field: value})


async def test_nonverbatim_reply_passes_graph_with_semantic_evidence(client):
    """원문 부분 문자열이 없어도 별도 의미 판정과 규칙 검사를 통과하면 stop으로 반환한다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    request = make_request(client)
    reply = "회장님의 법률 업무와 재산 관리를 곁에서 담당해 왔습니다. 오늘 찾아온 건 유언장을 변경하는 일을 처리하기 위해서입니다."
    assert all(fact.text not in reply for fact in request.allowed_facts)

    class ParaphraseModel:
        """두 승인 문장의 의미가 두 후보 문장에 있다는 판정을 명시적으로 제공한다.

        Args:
            없음.

        Returns:
            ParaphraseModel: 위 역할을 수행하도록 생성된 객체.
        """

        model_version = "paraphrase-contract-model"

        def __init__(self):
            """사용할 의존성과 초기 상태를 준비한다.

            Args:
                없음.

            Returns:
                None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.
            """
            self.purposes = []

        async def generate(self, messages, *, purpose="dialogue"):
            """호출 목적을 기록하여 생성과 검증의 디코딩 분리 연결을 검사한다.

            Args:
                messages: 모델에 전달할 역할별 프롬프트 목록.
                purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

            Returns:
                str: 호출 목적에 맞게 생성한 모델 출력 원문.
            """
            self.purposes.append(purpose)
            if purpose == "dialogue":
                return reply
            context = json.loads(messages[1]["content"])
            assert len(context["verification_units"]) == 2
            return json.dumps(
                {
                    "checks": [[0, True, [0]], [1, True, [1]]],
                    "has_contradiction": False,
                    "has_unsupported_claims": False,
                    "history_consistent": True,
                    "persona_consistent": True,
                    "uncertain": False,
                }
            )

    model = ParaphraseModel()
    response = await InterrogationGraph(
        client.app.state.service.settings, model
    ).generate(request)
    assert response.finish_reason == "stop"
    assert response.reply == reply
    assert response.used_fact_ids == ["yoon-profile"]
    assert model.purposes == ["dialogue", "verification"]


def test_style_freedom_does_not_authorize_new_quantities(client):
    """재서술을 허용해도 승인되지 않은 사건 금액을 추가할 권한은 없다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    request = make_request(client)
    assert (
        critical_claim_error(
            request, "저는 회장님의 업무를 맡아왔고 3억 원을 받았습니다."
        )
        == "unapproved_quantity_claim"
    )


def test_prompts_preserve_facts_but_allow_rewording(client):
    """생성에는 재서술 지침을, 검증에는 의미 동등 표현 허용 지침을 전달한다.

    Args:
        client: HTTP 요청을 실행하는 클라이언트.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    request = make_request(client)
    settings = client.app.state.service.settings
    messages = build_messages(request, settings)
    context = json.loads(messages[1]["content"])
    assert context["approved_facts"] == [
        fact.model_dump() for fact in request.allowed_facts
    ]
    assert context["required_fact_ids"] == request.required_fact_ids
    assert "항목 하나마다 완결된 대사 한 문장" in messages[0]["content"]
    assert "동의어·어순·종결어미" in messages[0]["content"]
    verification = build_verification_messages(request, settings, "대사 예시")
    assert "같은 의미이면 허용" in verification[0]["content"]


@pytest.mark.parametrize("style", ["  짧은 문장으로 답하세요.  ", "  ", None])
def test_character_speech_style_reaches_both_prompts(client, monkeypatch, style):
    """인물 지침이 생성·검증에 전달되고 미작성 상태에서는 공통 지침이 적용된다.

    Args:
        client: 실제 사건 카탈로그를 읽은 FastAPI 테스트 클라이언트.
        monkeypatch: 카탈로그를 테스트 중에만 수정하는 도구.
        style: 인물에게 설정할 문구 또는 필드 미설정을 나타내는 None.
    Returns:
        None: 생성과 검증의 페르소나에 설정한 문구가 반영됐는지 확인한다.
    """
    service = client.app.state.service
    person = service.catalog.people["yoon"]
    if style is None:
        monkeypatch.delitem(person, "speech_style", raising=False)
    else:
        monkeypatch.setitem(person, "speech_style", style)
    expected = (
        style or ""
    ).strip() or "존댓말. 승인 원문의 말투와 관찰 한계를 유지하세요."
    request = make_request(client)
    generation = build_messages(request, service.settings)
    verification = build_verification_messages(request, service.settings, "대사 예시")

    for messages in (generation, verification):
        persona = json.loads(messages[1]["content"])["persona"]
        assert persona == {
            "name": person["name"],
            "role": person["role"],
            "speech_style": expected,
        }
