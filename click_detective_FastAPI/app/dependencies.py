"""API 인증과 수사 서비스 접근을 공통으로 제공한다."""

import hmac

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.concurrency import run_in_threadpool

from .investigation.persistence.access import AccountAccess

bearer = HTTPBearer(auto_error=False)


async def authenticate(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)
):
    """Next.js 서버 전용 API 키를 검사한다. 브라우저에 이 키를 전달하지 않는다.

    Args:
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
        credentials (HTTPAuthorizationCredentials | None): Authorization 헤더에서 읽은 Bearer 인증 정보.

    Returns:
        None: 반환값 없음.
    """
    if credentials is None or not hmac.compare_digest(
        credentials.credentials, request.app.state.settings.api_key
    ):
        raise HTTPException(
            401,
            {"code": "SERVICE_AUTH_REQUIRED", "message": "서비스 인증이 필요합니다."},
            headers={"WWW-Authenticate": "Bearer"},
        )


def service(request: Request):
    """공통 인증을 통과한 API에 게임 서비스를 제공한다.

    Args:
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

    Returns:
        GameService: 요청을 받은 앱이 보관하는 수사 처리 서비스.
    """
    return request.app.state.service


def investigation_access(request: Request):
    """익명 토큰 또는 검증된 계정 문맥을 선택한다.

    Args:
        request: Next.js가 전달한 수사 접근 헤더를 담은 요청.

    Returns:
        str | AccountAccess: 저장소가 확인할 익명 토큰 또는 계정.
    """
    if "X-Access-Token" in request.headers:
        from .auth.routes import current_user

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
    game_service = service(request)
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
    return await service(request).change(game_id, access, command, action)
