"""모델이 인용문을 다시 쓰지 않고 후보 문장 번호를 선택하게 하는 의미 검증 계약."""

from dataclasses import dataclass
import re

from pydantic import Field, StrictBool, StrictInt

from .schemas import DTO


@dataclass(frozen=True)
class CandidateSentence:
    """서버가 원본 대사에서 잘라낸 문장. 번호가 원문의 실제 구간에 연결된다."""

    id: int
    start: int
    end: int
    text: str


def candidate_sentences(reply: str) -> list[CandidateSentence]:
    """문장 번호와 원문 위치를 만든다. 원문을 교정하거나 바꿔 인용을 맞추지 않는다."""
    result = []
    start = 0
    boundaries = [match.end() for match in re.finditer(r"(?<=[.!?。！？])\s+|\n+", reply)] + [len(reply)]
    for end in boundaries:
        left = start
        while left < end and reply[left].isspace():
            left += 1
        right = end
        while right > left and reply[right - 1].isspace():
            right -= 1
        if left < right:
            result.append(CandidateSentence(len(result), left, right, reply[left:right]))
        start = end
    return result


class SemanticReport(DTO):
    """짧은 검증 출력. 각 checks 항목은 [검증항목 번호, 포함 여부, 후보문장 번호 목록]."""

    checks: list[tuple[StrictInt, StrictBool, list[StrictInt]]] = Field(max_length=256)
    has_contradiction: StrictBool
    has_unsupported_claims: StrictBool
    history_consistent: StrictBool
    persona_consistent: StrictBool
    uncertain: StrictBool
