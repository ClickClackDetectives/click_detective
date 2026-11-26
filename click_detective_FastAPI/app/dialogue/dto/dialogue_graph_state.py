"""대화 생성 과정에서 주고받는 상태와 오류 형식을 정의한다."""

from dataclasses import dataclass
from typing import TypedDict

from pydantic import Field

from app.dialogue.dto.dialogue_reply_dto import (
    DTO,
    CharacterReplyRequest,
    CharacterReplyResponse,
    Identifier,
    ReplyText,
)
from app.dialogue.services.validation_agent.sentences.dialogue_verification_units import (
    VerificationUnit,
)
from app.investigation.dto.investigation_interrogation_plan_dto import ReplyPlan


class GeneratedReply(DTO):
    """모델이 직접 작성한 대사. 선택적 ID 자기 신고는 허용 범위만 검사하며 별도 검증한다.

    Args:
        reply (ReplyText): 의미를 검사하거나 문장으로 나눌 후보 대사.
        used_fact_ids (list[Identifier]): 응답에서 사용한 사실 식별자 목록.

    Returns:
        GeneratedReply: 위 역할을 수행하도록 생성된 객체.
    """

    reply: ReplyText
    used_fact_ids: list[Identifier] = Field(default_factory=list, max_length=10)


@dataclass
class SearchTurn:
    """게임 심문 한 건에서 검색으로 확정한 계획과 요청을 공유한다.

    Args:
        plan: 검색 전 게임 규칙으로 확인한 계획. 검색 후에는 기록할 최종 계획.
        request: 생성과 검증에 전달할 승인 사실과 대화 문맥.
        revealed: 심문을 시작할 때 이미 공개된 쟁점 ID.
        search_complete: 검색 단계가 끝나 생성 실패 복구가 가능한지 여부.

    Returns:
        SearchTurn: 생성 실패 시에도 확정된 승인 범위를 보존하는 요청별 문맥.
    """

    plan: ReplyPlan
    request: CharacterReplyRequest
    revealed: tuple[str, ...]
    search_complete: bool = False


class InterrogationState(TypedDict, total=False):
    """요청별 지역 상태. 원본 생성·검증 내용은 DB나 GameState에 저장하지 않는다.

    Args:
        request (CharacterReplyRequest): 승인 사실과 필수 사실 ID를 포함한 대화 요청.
        search_turn (SearchTurn): 게임 규칙이 승인한 검색 문맥. 게임 심문에만 사용한다.
        messages (list[dict[str, str]]): 모델에 전달할 역할별 프롬프트 목록.
        verification_units: 전처리에서 프롬프트와 검증에 공통으로 사용할 승인 문장.
        raw_output (str): 모델이 생성한 원문 대사.
        error_status (int | None): 모델 실행 실패의 HTTP 상태 코드.
        response (CharacterReplyResponse): 검사하거나 저장할 최종 대사 응답.

    Returns:
        InterrogationState: 위 역할을 수행하도록 생성된 객체.
    """

    request: CharacterReplyRequest
    search_turn: SearchTurn
    messages: list[dict[str, str]]
    verification_units: list[VerificationUnit]
    raw_output: str
    error_status: int | None
    response: CharacterReplyResponse
