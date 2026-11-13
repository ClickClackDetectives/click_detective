"""응답 검증과 고정 대사 조립. HTTP·로컬 모델이 공통으로 사용한다."""

from .schemas import CharacterReplyRequest, CharacterReplyResponse

NO_FACTS = "지금 말씀드릴 수 있는 추가 내용은 없습니다."
FIXED_MODEL_VERSION = "fixed-v1"


def validate_generation(
    request: CharacterReplyRequest,
    response: CharacterReplyResponse,
    *,
    require_verbatim: bool = True,
) -> None:
    """식별 정보·사실 ID·필수 사실을 검사한다. 고정 모드는 원문까지 대조한다. 실패하면 ValueError를 낸다.

    require_verbatim=False는 의미 검증을 별도로 수행하는 local 그래프에서만 사용한다.
    ID 검사만으로 내용이 참이라고 보장하지 않는다.
    이 검사는 임의의 추가 문장이 참인지 판별하지는 않는다. 그 범위는 조립 단계에서
    승인 원문만 사용하도록 제한한다.
    """
    request_identity = (request.request_id, request.suspect_id, request.state_revision)
    response_identity = (response.request_id, response.suspect_id, response.state_revision)
    if response_identity != request_identity:
        raise ValueError("Response identity mismatch")

    allowed_fact_texts = {fact.id: fact.text for fact in request.allowed_facts}
    used_fact_ids = set(response.used_fact_ids)
    required_fact_ids = set(request.required_fact_ids)

    has_duplicate_ids = len(response.used_fact_ids) != len(used_fact_ids)
    has_unapproved_ids = not used_fact_ids.issubset(allowed_fact_texts)
    if has_duplicate_ids or has_unapproved_ids:
        raise ValueError("Invalid used fact IDs")
    if not required_fact_ids.issubset(used_fact_ids):
        raise ValueError("Missing required facts")

    missing_fact_text = any(
        allowed_fact_texts[fact_id] not in response.reply
        for fact_id in response.used_fact_ids
    )
    if not response.reply.strip() or (require_verbatim and missing_fact_text):
        raise ValueError("Missing verbatim fact text")



def assemble_reply(request: CharacterReplyRequest) -> str:
    """모든 승인 사실을 순서대로 붙인다. 사실이 없으면 중립 대사를 준다."""
    if not request.allowed_facts:
        return NO_FACTS

    sentences = [fact.text for fact in request.allowed_facts]
    return " ".join(sentences)

