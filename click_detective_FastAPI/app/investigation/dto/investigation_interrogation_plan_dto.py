"""수사 규칙이 승인한 심문 계획을 대화 서비스에 전달한다."""

from dataclasses import dataclass


@dataclass
class ReplyPlan:
    """생성할 사실과 확정할 구조화 기록을 분리한 요청별 계획.

    Args:
        suspect_id (str): 심문 대상 인물의 식별자.
        question (str): 사용자가 입력한 질문 원문.
        topic (str | None): 질문에서 명시할 주제 식별자.
        entries (list[dict]): 게임 기록에 반영할 승인 진술.
        facts (list[dict]): 모델에 제공할 승인 사실.
        new_findings (list[dict]): 이번 심문으로 새로 공개할 쟁점.
        sources (list[dict]): 진술과 쟁점의 실제 근거.
        material_id (str | None): 이번 심문에 제시한 자료 식별자.

    Returns:
        ReplyPlan: 위 역할을 수행하도록 생성된 객체.
    """

    suspect_id: str
    question: str
    topic: str | None
    entries: list[dict]
    facts: list[dict]
    new_findings: list[dict]
    sources: list[dict]
    material_id: str | None
