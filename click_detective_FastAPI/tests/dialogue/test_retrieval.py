"""쉬운 반복문으로 바꾼 검색이 필수 사실과 원래 순서를 유지하는지 검사한다."""

from app.dialogue.preprocess_agent.rag.retriever import retrieve_approved_facts
from app.dialogue.schemas import Fact

from .test_verification_reports import profile_request


def facts_request(client):
    """점수가 다른 선택 사실과 점수가 없는 필수 사실을 준비한다.

    Args:
        client: 테스트 앱 클라이언트.

    Returns:
        CharacterReplyRequest: 검색 순서와 필수 사실 보존을 확인할 요청.
    """
    request = profile_request(client)
    facts = [
        Fact(id="low", text="정원에 있었습니다.", nature="본인 진술"),
        Fact(id="required", text="얼굴은 보지 못했습니다.", nature="본인 진술"),
        Fact(id="high", text="22시 식당에서 와인을 마셨습니다.", nature="본인 진술"),
        Fact(id="tie", text="22시 식당에서 와인을 마셨습니다.", nature="본인 진술"),
    ]
    return request.model_copy(
        update={
            "question": "22시 식당 와인",
            "allowed_facts": facts,
            "required_fact_ids": ["required"],
        }
    )


def test_retrieval_preserves_required_fact_and_stable_score_order(client):
    """점수가 같으면 먼저 승인된 사실을 고르고 필수 사실은 점수와 무관하게 유지한다.

    Args:
        client: 검색 입력을 만들 테스트 앱 클라이언트.

    Returns:
        None: 필수 사실과 동점 중 먼저 나온 선택 사실이 원래 순서로 반환되는지 검사한다.
    """
    request = facts_request(client)
    result = retrieve_approved_facts(request, top_k=1)
    ids = []
    for fact in result.selected_facts:
        ids.append(fact.id)
    assert ids == ["required", "high"]
    assert result.hits[0].reason == "required"
    assert result.hits[1].reason == "related"
    result.selected_facts[0].text = "검색 결과만 수정"
    assert request.allowed_facts[1].text == "얼굴은 보지 못했습니다."


def test_zero_optional_limit_keeps_required_fact(client):
    """선택 사실 수가 0이어도 필수 사실을 삭제하지 않는다.

    Args:
        client: 테스트 앱 클라이언트.

    Returns:
        None: 점수가 없는 필수 사실만 남는지 검사한다.
    """
    result = retrieve_approved_facts(facts_request(client), top_k=0)
    assert len(result.selected_facts) == 1
    assert result.selected_facts[0].id == "required"


def test_disabled_retrieval_keeps_every_approved_fact(client):
    """검색을 끄면 관련성과 상관없이 승인된 사실 전체를 보존한다.

    Args:
        client: 테스트 앱 클라이언트.

    Returns:
        None: 승인 원래 순서와 검색 비활성화 이유를 확인한다.
    """
    request = facts_request(client)
    result = retrieve_approved_facts(request, top_k=0, enabled=False)
    assert list(result.selected_facts) == request.allowed_facts
    for hit in result.hits:
        assert hit.reason == "disabled"
        assert hit.score == 0
