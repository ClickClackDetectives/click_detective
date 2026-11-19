"""모델이 인용문을 다시 쓰지 않고 후보 문장 번호를 선택하게 하는 의미 검증 계약."""

import re
from dataclasses import dataclass

from pydantic import Field, StrictBool, StrictInt

from ..schemas import DTO


@dataclass(frozen=True)
class CandidateSentence:
    """서버가 원본 대사에서 잘라낸 문장. 번호가 원문의 실제 구간에 연결된다.

    Args:
        id (int): 항목을 구분하는 식별자.
        start (int): 원문에서 문장이 시작하는 위치.
        end (int): 원문에서 문장이 끝나는 위치.
        text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

    Returns:
        CandidateSentence: 위 역할을 수행하도록 생성된 객체.
    """

    id: int
    start: int
    end: int
    text: str


def candidate_sentences(reply: str) -> list[CandidateSentence]:
    """문장 번호와 원문 위치를 만든다. 원문을 교정하거나 바꿔 인용을 맞추지 않는다.

    Args:
        reply (str): 의미를 검사하거나 문장으로 나눌 후보 대사.

    Returns:
        list[CandidateSentence]: 후보 문장의 번호, 원문 위치와 텍스트.
    """
    result = []
    start = 0
    boundaries = [
        match.end() for match in re.finditer(r"(?<=[.!?。！？])\s+|\n+", reply)
    ] + [len(reply)]
    for end in boundaries:
        left = start
        while left < end and reply[left].isspace():
            left += 1
        right = end
        while right > left and reply[right - 1].isspace():
            right -= 1
        if left < right:
            result.append(
                CandidateSentence(len(result), left, right, reply[left:right])
            )
        start = end
    return result


class SemanticReport(DTO):
    """짧은 검증 출력. 각 checks 항목은 [검증항목 번호, 포함 여부, 후보문장 번호 목록].

    Args:
        checks (list[tuple[StrictInt, StrictBool, list[StrictInt]]]): 승인 항목별 포함 여부와 근거 문장 번호 목록.
        has_contradiction (StrictBool): 승인 내용과 모순되는지 여부.
        has_unsupported_claims (StrictBool): 승인되지 않은 추가 주장이 있는지 여부.
        history_consistent (StrictBool): 이전 대화와 일관된지 여부.
        persona_consistent (StrictBool): 인물 설정과 일관된지 여부.
        uncertain (StrictBool): 의미 판정이 불확실한지 여부.

    Returns:
        SemanticReport: 위 역할을 수행하도록 생성된 객체.
    """

    checks: list[tuple[StrictInt, StrictBool, list[StrictInt]]] = Field(max_length=256)
    has_contradiction: StrictBool
    has_unsupported_claims: StrictBool
    history_consistent: StrictBool
    persona_consistent: StrictBool
    uncertain: StrictBool
