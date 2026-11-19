"""실제 모델을 사용하는 내부 에이전트 검사 API."""

from fastapi import APIRouter, Depends, HTTPException, Request

from ..dependencies import authenticate, service
from .schemas import CharacterReplyRequest, CharacterReplyResponse

router = APIRouter(dependencies=[Depends(authenticate)], include_in_schema=False)


def agent_test_service(request: Request):
    """검사 API 활성화 여부와 로컬 그래프를 확인한다.

    Args:
        request: 실행 중인 앱에 접근할 HTTP 요청.

    Returns:
        GameService: 검사에 사용할 설정과 그래프를 보관한 서비스.
    """
    game_service = service(request)
    if not game_service.settings.agent_test_enabled:
        raise HTTPException(404, "agent_test_disabled")
    if game_service.settings.generation_mode != "local" or game_service.graph is None:
        raise HTTPException(503, "local_agent_graph_unavailable")
    return game_service


@router.get("/internal/agent-test")
async def agent_test_config(request: Request):
    """배치 전에 실제 서버 버전과 진단 설정을 확인한다.

    Args:
        request: 실행 중인 앱에 접근할 HTTP 요청.

    Returns:
        dict: 검증 버전과 진단 활성화 여부.
    """
    settings = agent_test_service(request).settings
    return {
        "validation_agent_version": settings.validation_agent_version,
        "diagnostics_enabled": settings.diagnostics_enabled,
    }


@router.post("/internal/agent-test")
async def run_agent_test(
    command: CharacterReplyRequest, request: Request
) -> CharacterReplyResponse:
    """테스트 문맥으로 서버에 로드된 대화 그래프를 직접 실행한다.

    Args:
        command: 테스트용으로 제공한 승인 사실과 대화 문맥.
        request: 실행 중인 서버의 설정과 그래프에 접근할 HTTP 요청.

    Returns:
        CharacterReplyResponse: 세 에이전트가 처리한 최종 대화 응답.
    """
    return await agent_test_service(request).graph.generate(command)
