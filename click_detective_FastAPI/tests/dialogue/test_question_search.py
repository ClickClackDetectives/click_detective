"""심문 API에서 첫 진술 선택과 공개 범위를 검사한다."""

from uuid import uuid4

import pytest

from app.dialogue.interrogation_graph import InterrogationGraph
from app.dialogue.preprocess_agent.question_search import (
    OFF_TOPIC,
    OVERVIEW,
    QuestionSearch,
    public_candidates,
)
from app.dialogue.reply_validation import NO_FACTS
from tests.dialogue.models import ApprovedModel


class FakeIndex:
    """벡터 모델 없이 진술 선택 정책과 API 연결을 검증한다.

    Args:
        없음.
    Returns:
        FakeIndex: 요청과 후보를 기록하는 인덱스.
    """

    def __init__(self):
        """기본 점수와 요청 기록을 준비한다.

        Args:
            없음.
        Returns:
            None: 초기 상태를 저장한다.
        """
        self.scores = {}
        self.passages = []
        self.questions = []

    def score(self, question, texts):
        """후보별로 테스트가 정한 유사도를 반환한다.

        Args:
            question: 원문 질문.
            texts: 승인된 검색용 문장.
        Returns:
            dict: 문장별 유사도.
        """
        self.questions.append(question)
        self.passages.extend(texts)
        return {text: self.scores.get(text, 0.7) for text in texts}


@pytest.fixture
def vector_route(client, monkeypatch):
    """실제 심문 경로에 검색기와 모델 호출 기록기를 연결한다.

    Args:
        client: FastAPI 테스트 클라이언트.
        monkeypatch: 서버 의존성을 교체하는 도구.
    Returns:
        tuple: 심문 서비스, 모의 인덱스, 대사 생성·검증 모델.
    """
    service = client.app.state.service
    model = ApprovedModel()
    index = FakeIndex()
    monkeypatch.setattr(service.settings, "generation_mode", "local")
    monkeypatch.setattr(service, "graph", InterrogationGraph(service.settings, model))
    monkeypatch.setattr(
        service,
        "question_search",
        QuestionSearch(service.catalog, service.settings, index),
    )
    return service, index, model


def ask(api, game, question, **fields):
    """초기 수사 상태에서 윤재혁에게 질문한다.

    Args:
        api: HTTP 호출 함수.
        game: 초기 수사 ID와 토큰.
        question: 자유 질문 원문.
        fields: 필요할 때 주는 주제나 다른 인물 ID.
    Returns:
        dict: 성공한 심문의 응답 본문.
    """
    response = api(
        "POST",
        f"/v1/games/{game['game_id']}/interrogations",
        {
            "request_id": str(uuid4()),
            "expected_revision": 0,
            "suspect_id": "yoon",
            "question": question,
            **fields,
        },
        game["game_token"],
    )
    assert response.status_code == 200, response.text
    return response.json()["result"]


@pytest.mark.parametrize(
    "question",
    [
        "코 고는 소리를 들었나요?",
        "혹시 무슨 소리 못 들으셨나요?",
        "혹시 코골이 소리 들으셧나여?",
    ],
)
def test_vector_search_selects_the_fact_before_generation(
    api, game, vector_route, monkeypatch, question
):
    """원문을 바로 검색에 사용하고 선택된 진술만 생성·검증과 수사 기록에 넘긴다.

    Args:
        api: 심문 API 호출 함수.
        game: 초기 수사 상태.
        vector_route: 인덱스와 모델 호출 기록을 제공하는 구성.
        monkeypatch: 기존 정규식 경로를 호출 시 실패하도록 교체한다.
        question: 표현이 다른 소리 관련 질문.
    Returns:
        None: 검색 입력과 승인 원문이 전달되는 경로를 검사한다.
    """
    service, index, model = vector_route
    monkeypatch.delattr(type(service.planner), "resolve_topic")
    monkeypatch.delattr(type(service.planner), "free_entries")
    snoring = service.planner.movement("yoon", [])[2]
    assert snoring["key"] == "snoring"
    passage = f"{snoring['title']} {snoring['time']}. {snoring['text']}"
    index.scores[passage] = 0.9

    assert ask(api, game, question)["used_fact_ids"] == ["yoon-snoring"]
    assert index.questions == [question]
    assert passage in index.passages
    assert snoring["text"] not in index.passages
    generation, verification = model.calls
    assert generation["question"] == question
    assert generation["approved_facts"][0]["text"] == snoring["text"]
    assert verification["required_fact_ids"] == ["yoon-snoring"]
    state = service.read(game["game_id"], game["game_token"])
    assert state["statements"]["yoon-snoring"]["excerpt"] == snoring["text"]
    assert state["revealed"] == []


@pytest.mark.parametrize(
    ("question", "reject", "minute_conflict"),
    [
        ("오늘 점심 뭐 드셨어요?", True, False),
        ("23:30에 코 고는 소리를 들었나요?", False, True),
        ("내일 날씨가 어때요?", False, False),
    ],
)
def test_no_match_skips_both_llm_calls(
    api, game, vector_route, question, reject, minute_conflict
):
    """관련 없음, 시각 불일치, 낮은 점수는 고정 응답으로 처리한다.

    Args:
        api: 심문 API 호출 함수.
        game: 초기 수사 상태.
        vector_route: 검색기와 호출 기록.
        question: 검색 실패를 기대하는 원문.
        reject: 사건 외 비교 문장을 1위에 올린다.
        minute_conflict: 질문과 시각이 다른 진술을 1위에 올린다.
    Returns:
        None: 원문 사용, LLM 호출, 진술 기록이 없는지 검사한다.
    """
    service, index, model = vector_route
    if reject or minute_conflict:
        snoring = service.planner.movement("yoon", [])[2]
        index.scores[f"{snoring['title']} {snoring['time']}. {snoring['text']}"] = 0.9
    if reject:
        index.scores[OFF_TOPIC] = 0.92
    result = ask(api, game, question)
    assert result["reply"] == NO_FACTS
    assert result["used_fact_ids"] == model.calls == []
    assert index.questions == [question]
    assert not service.read(game["game_id"], game["game_token"])["statements"]


@pytest.mark.parametrize("explicit", [False, True])
def test_full_timeline_keeps_structured_path(api, game, vector_route, explicit):
    """자유 동선은 벡터로 선택하고 명시 주제는 곧바로 기존 원문을 고른다.

    Args:
        api: 심문 API 호출 함수.
        game: 초기 수사 상태.
        vector_route: 인덱스와 모델 호출 기록을 제공하는 구성.
        explicit: 플레이어가 동선 주제 버튼을 선택했는지 여부.
    Returns:
        None: 승인된 동선 원문 전체와 검색 우회 여부를 검증한다.
    """
    service, index, _ = vector_route
    index.scores[OVERVIEW] = 0.93
    question = "그날 밤 어떤 순서로 움직였나요?"
    result = ask(api, game, question, topic_id="movement" if explicit else None)
    assert result["used_fact_ids"] == [
        "yoon-" + entry["key"] for entry in service.planner.movement("yoon", [])
    ]
    assert index.questions == ([] if explicit else [question])


def test_candidates_keep_revealed_admissions_scoped_to_the_speaker(vector_route):
    """미공개 쟁점과 다른 사람의 인정 원문을 후보에서 제외한다.

    Args:
        vector_route: 사건 카탈로그가 설정된 서비스.
    Returns:
        None: 쟁점 공개 후 현재 인물에게만 추가되는지 검증한다.
    """
    service, _, _ = vector_route
    before = public_candidates(service.catalog, "yoon", [])
    after = public_candidates(
        service.catalog, "yoon", ["yoon_visit", "yoon_money", "cha_identity"]
    )
    keys = {entry["key"] for item in after for entry in item.entries}
    assert not any(
        entry["key"].startswith("admit-") for item in before for entry in item.entries
    )
    assert "admit-yoon_visit" in keys
    assert "admit-cha_identity" not in keys
    money = service.catalog.testimony["admissionEntries"]["yoon_money"]
    assert any(item.text == f"{money['title']}. {money['text']}" for item in after)
