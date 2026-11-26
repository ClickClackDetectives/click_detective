"""서버가 시작될 때 사건, 수사 서비스와 대화 모델을 준비한다."""

from contextlib import AsyncExitStack, asynccontextmanager

from app.auth.providers.auth_provider import open_auth_service
from app.cases.providers.cases_provider import build_catalog_service
from app.dialogue.providers.dialogue_provider import open_reply_service
from app.investigation.providers.investigation_provider import (
    build_game_service,
    open_investigation_repository,
)

from .runtime_settings import Settings


@asynccontextmanager
async def lifespan(app, *, settings: Settings | None = None):
    """도메인 provider에서 앱의 서비스를 준비하고 종료 시 자원을 해제한다.

    Args:
        app: 설정과 서비스를 보관할 FastAPI 애플리케이션.
        settings: 명시적으로 주입한 설정. None이면 앱 시작 시 환경 설정을 읽는다.

    Returns:
        AsyncIterator[None]: 앱의 시작 준비를 끝낸 뒤 실행을 서버에 넘기는 비동기 반복자.
    """
    config = settings
    if config is None:
        config = Settings()
    catalog_service = build_catalog_service(config.data_dir)
    async with AsyncExitStack() as resources:
        repository = await resources.enter_async_context(
            open_investigation_repository(config)
        )
        auth = await resources.enter_async_context(open_auth_service(config))
        reply_service = await resources.enter_async_context(
            open_reply_service(config, catalog_service.repository)
        )
        app.state.settings = config
        app.state.catalog_service = catalog_service
        app.state.reply_service = reply_service
        app.state.service = build_game_service(
            config, catalog_service, repository, reply_service
        )
        app.state.auth = auth
        yield
