"""수사 요청의 접근 권한과 상태 변경 경로를 연결한다."""

from fastapi import Request
from starlette.concurrency import run_in_threadpool

from app.investigation.providers.investigation_provider import get_game_service
from app.investigation.repositories.investigation_access import AccountAccess


def investigation_access(request: Request):
    """익명 토큰 또는 검증된 계정 문맥을 선택한다.

    Args:
        request: Next.js가 전달한 수사 접근 헤더를 담은 요청.

    Returns:
        str | AccountAccess: 저장소가 확인할 익명 토큰 또는 계정.
    """
    if "X-Access-Token" in request.headers:
        from app.auth.controllers.auth_request_context import current_user

        return AccountAccess(current_user(request)["id"])
    return request.headers.get("X-Game-Token", "")


def game(request: Request, game_id: str):
    """게임 토큰과 버전으로 접근 권한을 확인한다.

    Args:
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
        game_id (str): 조회하거나 변경할 수사의 식별자.

    Returns:
        dict: 접근 토큰과 사건 버전을 확인한 내부 수사 상태.
    """
    game_service = get_game_service(request)
    return game_service.read(game_id, investigation_access(request))


async def mutate(request, game_id, command, action):
    """모든 변경 API가 같은 중복·revision·확정 경로를 사용한다.

    Args:
        request: 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
        game_id: 조회하거나 변경할 수사의 식별자.
        command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
        action: 실행할 수사 행동 이름. 예: interrogate, examine.

    Returns:
        dict: 확정된 행동 결과, 요청 ID와 공개 수사 상태.
    """
    access = await run_in_threadpool(investigation_access, request)
    return await get_game_service(request).change(game_id, access, command, action)
