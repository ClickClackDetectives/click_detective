"""두 v2 정책의 출력과 게임 저장 경로를 검사한다."""

import json
import sys
from importlib import import_module
from types import ModuleType
from unittest.mock import Mock

import pytest

from app.dialogue.dto.dialogue_reply_dto import CharacterReplyRequest
from app.dialogue.services.reply.dialogue_interrogation_graph import InterrogationGraph
from app.dialogue.services.validation_agent.evidence import dialogue_rules as rules
from app.dialogue.services.validation_agent.evidence.dialogue_rules import (
    preserves_anchors,
)
from app.dialogue.services.validation_agent.output.dialogue_neutral import (
    NEUTRAL_REPLIES,
)
from app.runtime.runtime_settings import Settings
from scripts.live_dialogue.agent_inputs import load_agent_inputs


class ScriptedModel:
    """생성과 판정에 서로 다른 고정 출력을 제공한다.

    Args:
        dialogue: 생성 단계에서 반환할 후보 대사.
        judgment: 검증 단계에서 반환할 판정 JSON.

    Returns:
        ScriptedModel: 호출 목적의 순서를 기록하는 모델.
    """

    model_version = "v2-test-model"

    def __init__(self, dialogue, judgment=None):
        """검사에 사용할 대사와 판정을 준비한다.

        Args:
            dialogue: 생성 대사.
            judgment: 검증 결과 JSON으로 변환할 객체.

        Returns:
            None: 출력값과 호출 기록을 초기화한다.
        """
        self.dialogue = dialogue
        self.judgment = judgment
        self.calls = []

    async def generate(self, messages, *, purpose="dialogue"):
        """현재 호출에 해당하는 고정 출력을 반환한다.

        Args:
            messages: 생성 또는 검증 프롬프트.
            purpose: 모델 호출의 목적.

        Returns:
            str: 대사 원문 또는 검증 판정 JSON.
        """
        self.calls.append(purpose)
        return self.dialogue if purpose == "dialogue" else json.dumps(self.judgment)


async def test_delivers_only_verified_facts(fixture_settings):
    """유효한 방문 목적을 남기고 잘못된 시각은 부분 중립으로 처리한다.

    Args:
        fixture_settings: 모의 실행에 사용할 설정.

    Returns:
        None: 부분 응답과 전달 사실 ID를 검사한다.
    """
    body = load_agent_inputs(None, 1)[0]
    body["question"] = "방문 목적과 도착 시각을 알려 주세요."
    body["allowed_facts"] = [
        body["allowed_facts"][0],
        {"id": "arrival", "text": "오후 6시에 도착했습니다.", "nature": "본인 진술"},
    ]
    body["required_fact_ids"] = ["visit-reason", "arrival"]
    request = CharacterReplyRequest.model_validate(body)
    settings = fixture_settings
    line = "예약했던 책을 수령하러 왔습니다."
    model = ScriptedModel(f"{line} 오후 7시에 도착했습니다.", {"matches": [[0, [0]]]})
    reply = await InterrogationGraph(settings, model).generate(request)
    assert reply.reply == f"{line} 도착 시각은 지금 말씀드리기 어렵습니다."
    assert reply.finish_reason == "partial"
    assert reply.used_fact_ids == ["visit-reason"]
    assert model.calls == ["dialogue", "verification"]


async def test_public_scope_checks_no_fact_candidates(fixture_settings):
    """승인 사실 없는 후보를 생성하고 질문의 전제를 긍정하지 않는다.

    Args:
        fixture_settings: 모의 실행에 사용할 설정.

    Returns:
        None: 명확한 확인 질문은 통과하고 근거 없는 긍정은 중립으로 바뀐다.
    """
    body = load_agent_inputs(None, 1)[0]
    body.update(
        allowed_facts=[],
        required_fact_ids=[],
        question="오후 9시에 서재에 있었죠?",
    )
    request = CharacterReplyRequest.model_validate(body)
    settings = fixture_settings
    for candidate, reason in [
        ("어떤 시간대를 말씀하시는 건가요?", "stop"),
        ("네, 맞아요.", "neutral"),
    ]:
        model = ScriptedModel(candidate, {"allowed": True})
        response = await InterrogationGraph(settings, model).generate(request)
        assert response.finish_reason == reason
        assert response.used_fact_ids == []
        assert model.calls == ["dialogue"]
        if reason == "neutral":
            assert response.reply in NEUTRAL_REPLIES["timeline"]


def test_neutral_does_not_unlock_unspoken_finding(client, play, monkeypatch):
    """실제 심문 API에서 중립 대사가 미전달 쟁점을 공개하지 않는지 확인한다.

    Args:
        client: 케이스 데이터를 사용하는 테스트 앱.
        play: 수사를 진행하는 API 도우미.
        monkeypatch: 기존 설정을 일시 변경하는 도구.

    Returns:
        None: 중립 응답을 저장하되 승인된 쟁점이 남아 있는지 검사한다.
    """
    service = client.app.state.service
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    model = ScriptedModel("할 말이 없어요.")
    monkeypatch.setattr(
        service.reply_service, "graph", InterrogationGraph(service.settings, model)
    )
    play.act("examinations", evidence_id="S-Y")
    result = play.act(
        "interrogations",
        suspect_id="yoon",
        question="장부의 경위를 설명하세요.",
        material_id="S-Y",
    )
    assert result["result"]["finish_reason"] == "neutral"
    assert result["result"]["used_fact_ids"] == []
    assert result["state"]["revealed"] == []
    assert result["state"]["findingDetails"] == []
    assert model.calls == ["dialogue"]


def test_legacy_validator_setting_does_not_select_an_implementation(tmp_path):
    """이전 환경 파일의 검증 버전 값이 단일 검증 구현에 영향을 주지 않는지 확인한다.

    Args:
        tmp_path: 이전 환경 설정 파일을 작성할 임시 디렉터리.

    Returns:
        None: 설정이 로드되며 검증 버전 필드가 없음을 확인한다.
    """
    path = tmp_path / ".env"
    path.write_text("CLICK_VALIDATION_AGENT_VERSION=v1\n")
    settings = Settings(api_key="test-service-secret", _env_file=path)
    assert "validation_agent_version" not in settings.model_dump()


def test_rejects_changed_meridiem():
    """숫자가 같아도 오전·오후를 바꾼 대사는 거절한다.

    Args:
        없음.

    Returns:
        None: 시각의 오전·오후 변경을 검사한다.
    """
    assert not preserves_anchors("오후 6시에 도착했습니다.", "오전 6시에 도착했습니다.")


async def test_embeds_candidates_and_facts_in_one_batch(fixture_settings, monkeypatch):
    """검증 에이전트가 임베딩을 한 번 계산하고 근거 없는 문장을 제거하는지 확인한다.

    Args:
        fixture_settings: 테스트 서버 설정.
        monkeypatch: SentenceTransformer 모듈을 모의 구현으로 교체하는 도구.

    Returns:
        None: 임베딩 배치, 최종 대사 및 모델 호출 순서를 검사한다.
    """
    numpy = pytest.importorskip("numpy")
    encoder = Mock()
    encoder.encode.return_value = numpy.array([[1.0, 0.0], [0.0, 1.0]])
    constructor = Mock(return_value=encoder)
    module = rules
    if not hasattr(rules, "SentenceTransformer"):
        try:
            module = import_module("sentence_transformers")
        except ImportError:
            module = ModuleType("sentence_transformers")
            monkeypatch.setitem(sys.modules, "sentence_transformers", module)
    monkeypatch.setattr(module, "SentenceTransformer", constructor, raising=False)
    body = load_agent_inputs(None, 1)[0]
    body["allowed_facts"] = body["allowed_facts"][:1]
    approved = body["allowed_facts"][0]["text"]
    extra = "누군가 전구를 깨뜨렸습니다."
    model = ScriptedModel(f"{approved} {extra}")
    settings = fixture_settings.model_copy(
        update={
            "validation_similarity_backend": "sentence_transformer",
        }
    )
    graph = InterrogationGraph(settings, model)
    reply = await graph.generate(CharacterReplyRequest.model_validate(body))
    constructor.assert_called_once_with(
        settings.validation_embedding_model,
        device="cpu",
        local_files_only=True,
        trust_remote_code=False,
    )
    encoder.encode.assert_called_once_with(
        [approved, extra], normalize_embeddings=True, show_progress_bar=False
    )
    assert reply.finish_reason == "stop"
    assert reply.reply == approved
    assert model.calls == ["dialogue"]
