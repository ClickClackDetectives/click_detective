"""FastAPI 애플리케이션을 만들고 도메인별 API를 연결한다."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.investigation.api.material_routes import router as material_router
from app.investigation.api.routes import router as investigation_router
from app.investigation.api.view_routes import router as view_router

from .bootstrap import lifespan
from .cases.routes import router as case_router
from .config import Settings
from .dialogue.test_routes import router as agent_test_router


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
        lifespan=lifespan,
        description="사건 데이터·규칙·수사 저장·양자화 Qwen 대사 생성을 담당하는 백엔드",
    )
    app.state.initial_settings = settings

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request, error):
        """원문·토큰을 오류 응답에 복사하지 않고 위치·오류 종류만 반환한다.

        Args:
            request: 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
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
        case_router,
        investigation_router,
        material_router,
        view_router,
        agent_test_router,
    ):
        app.include_router(router)
    return app


app = create_app()
