"""계정이 소유한 수사 목록과 익명 수사 연결을 제공한다."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.auth.controllers.auth_request_context import current_user
from app.investigation.dto.investigation_command_dto import DTO
from app.investigation.providers.investigation_provider import get_game_service
from app.runtime.runtime_auth import authenticate

router = APIRouter(prefix="/v1/investigations", dependencies=[Depends(authenticate)])


class Claim(DTO):
    """현재 브라우저가 계정에 연결할 수사의 입력을 검증한다.

    Args:
        game_id: 연결할 익명 수사의 UUID.

    Returns:
        Claim: 형식을 검사한 연결 요청.
    """

    game_id: UUID


@router.get("", tags=["수사 계정"])
def list_investigations(
    request: Request,
    cursor: Annotated[str | None, Query(max_length=250)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
):
    """세션이 활성화된 사용자의 수사를 최근 갱신 순으로 조회한다.

    Args:
        request: 계정 접근 헤더와 서비스가 연결된 요청.
        cursor: 직전 페이지가 반환한 위치 또는 첫 페이지에서 None.
        limit: 한 페이지에 반환할 수사 수.

    Returns:
        dict: 공개 수사 요약 목록과 다음 페이지 커서.
    """
    account = current_user(request)
    return get_game_service(request).repository.list_owned(account["id"], cursor, limit)


@router.post("/claim", tags=["수사 계정"])
def claim_investigation(command: Claim, request: Request):
    """익명 토큰으로 수사를 확인해 현재 계정에 연결한다.

    Args:
        command: 연결할 익명 수사 ID가 포함된 요청.
        request: 세션과 익명 토큰이 포함된 요청.

    Returns:
        dict: 계정으로 연결한 수사의 공개 요약.
    """
    account = current_user(request)
    return get_game_service(request).repository.claim(
        str(command.game_id), request.headers.get("X-Game-Token", ""), account["id"]
    )
