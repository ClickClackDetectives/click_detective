"""복합 승인 사실을 문장별 검증 항목으로 나눈다. 공개 권한과 원래 사실 ID는 바꾸지 않는다."""

from dataclasses import dataclass
import re

from .schemas import CharacterReplyRequest


@dataclass(frozen=True)
class VerificationUnit:
    """한 문장의 검증 ID와 원래 사실 ID. 일부 문장만 통과한 사실은 전체 통과가 아니다."""

    id: str
    fact_id: str
    text: str


def build_verification_units(request: CharacterReplyRequest) -> list[VerificationUnit]:
    """문장 종결 부호 뒤의 공백·줄바꿈만 구분한다. 조사·부정·문장 내부 절은 자르지 않는다.

    이는 완전한 의미 원자화가 아니다. 한 문장 안의 행위자·시각·부정까지 확인하는
    책임은 의미 검증에 남는다. 원문 순서와 모든 텍스트 조각을 보존한다.
    """
    units = []
    for fact in request.allowed_facts:
        sentences = [text.strip() for text in re.split(r"(?<=[.!?。！？])\s+|\n+", fact.text) if text.strip()]
        for sentence in sentences:
            units.append(VerificationUnit(id=f"unit-{len(units)}", fact_id=fact.id, text=sentence))
    return units
