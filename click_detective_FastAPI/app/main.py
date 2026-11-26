"""FastAPI 애플리케이션을 만들고 도메인별 API를 연결한다."""

from functools import partial

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.auth.controllers.auth_controller import router as auth_router
from app.dialogue.controllers.dialogue_agent_test_controller import (
    router as agent_test_router,
)
from app.investigation.controllers.investigation_account_controller import (
    router as account_router,
)
from app.investigation.controllers.investigation_game_controller import (
    router as investigation_router,
)
from app.investigation.controllers.investigation_material_controller import (
    router as material_router,
)
from app.investigation.controllers.investigation_view_controller import (
    router as view_router,
)

from .cases.controllers.cases_controller import router as case_router
from .runtime.runtime_lifespan import lifespan
from .runtime.runtime_settings import Settings


def create_app(settings: Settings | None = None):
    """앱을 구성한다. 실제 데이터·DB·모델 준비는 lifespan에서 수행한다.

    Args:
        settings (Settings | None): 모델 실행과 검색에 사용할 설정.

    Returns:
        FastAPI: 도메인별 API와 시작 절차를 연결한 애플리케이션.
    """
    app = FastAPI(
        title="Click Detective",
        version="0.1.0",
        lifespan=partial(lifespan, settings=settings),
        description="사건 데이터·규칙·수사 저장·양자화 Qwen 대사 생성을 담당하는 백엔드",
    )

    @app.exception_handler(RequestValidationError)
    async def invalid_input(_request, error):
        """원문·토큰을 오류 응답에 복사하지 않고 위치·오류 종류만 반환한다.

        Args:
            _request: FastAPI가 오류 처리기에 전달하는 HTTP 요청.
            error: 현재 처리할 예외 또는 입력 검증 오류.

        Returns:
            JSONResponse: 민감한 원문을 제외하고 오류 위치·종류만 담은 HTTP 422 응답.
        """
        return JSONResponse(
            status_code=422,
            content={
                "detail": [
                    {"loc": item["loc"], "type": item["type"]}
                    for item in error.errors()
                ]
            },
        )

    @app.exception_handler(PyMongoError)
    async def investigation_store_unavailable(request, error):
        """수사 저장 오류를 재시도 가능한 공개 응답으로 변환한다.

        Args:
            request: 저장소 오류가 발생한 요청.
            error: 접속 정보가 포함될 수 있는 저장소 예외.

        Returns:
            JSONResponse: 기존 요청 UUID를 유지해 재시도할 수 있는 503 응답.
        """
        return JSONResponse(
            status_code=503,
            content={
                "detail": {
                    "code": "INVESTIGATION_STORE_UNAVAILABLE",
                    "message": "수사 저장소에 연결할 수 없습니다. 같은 요청으로 다시 확인하세요.",
                }
            },
        )

    @app.middleware("http")
    async def no_store(request, call_next):
        """수사별 데이터가 브라우저나 프록시의 공용 캐시에 남지 않게 한다.

        Args:
            request: 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
            call_next: 다음 HTTP 처리 단계로 요청을 전달하는 함수.

        Returns:
            Response: Cache-Control: no-store 헤더를 추가한 HTTP 응답.
        """
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/healthz", tags=["운영"])
    async def health():
        """서버 시작 완료를 확인한다. 모델 품질 시험을 실행하지 않는다.

        Args:
            없음.

        Returns:
            dict[str, str]: 서버 준비 상태를 나타내는 status=ok 정보.
        """
        return {"status": "ok"}

    for router in (
        auth_router,
        account_router,
        case_router,
        investigation_router,
        material_router,
        view_router,
        agent_test_router,
    ):
        app.include_router(router)
    return app


app = create_app()
