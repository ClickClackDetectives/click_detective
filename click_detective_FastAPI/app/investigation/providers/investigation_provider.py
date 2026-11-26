"""수사 저장소와 게임 서비스를 앱 시작 시 조립한다."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Request

from app.cases.services.cases_catalog_service import CatalogService
from app.dialogue.services.reply.dialogue_reply_service import ReplyService
from app.investigation.repositories.investigation_mongo_repository import (
    MongoRepository,
)
from app.investigation.services.interrogation.investigation_interrogation_planner import (
    Planner,
)
from app.investigation.services.investigation_game_service import GameService
from app.investigation.services.rules.investigation_rule_engine import Engine
from app.investigation.services.views.investigation_presenter import Presenter
from app.runtime.runtime_settings import Settings


@asynccontextmanager
async def open_investigation_repository(
    config: Settings,
) -> AsyncIterator[MongoRepository]:
    """현재 앱의 MongoDB 수사 저장소를 열고 종료할 때 연결을 닫는다.

    Args:
        config: MongoDB 연결 문자열과 데이터베이스 이름을 담은 설정.

    Returns:
        AsyncIterator[MongoRepository]: 앱 수명 동안 사용할 수사 저장소.

    Raises:
        RuntimeError: MongoDB 연결 문자열이 설정되지 않은 경우.
    """
    if config.mongo_uri is None:
        raise RuntimeError("수사를 저장할 CLICK_MONGO_URI를 설정하세요.")
    repository = await asyncio.to_thread(
        MongoRepository, config.mongo_uri.get_secret_value(), config.mongo_database
    )
    try:
        yield repository
    finally:
        await asyncio.to_thread(repository.close)


def build_game_service(
    config: Settings,
    catalog_service: CatalogService,
    repository: MongoRepository,
    reply_service: ReplyService,
) -> GameService:
    """규칙 엔진, 승인 계획, 화면 조립과 대화 서비스를 수사 흐름에 연결한다.

    Args:
        config: 수사와 대화에 적용할 앱 설정.
        catalog_service: 앱 시작 시 준비한 사건 카탈로그 서비스.
        repository: 수사 상태를 영속화할 MongoDB 저장소.
        reply_service: 승인된 문맥에서 대사를 생성할 대화 서비스.

    Returns:
        GameService: 생성·조회·수사 행동을 처리하는 서비스.
    """
    catalog = catalog_service.repository
    engine = Engine(catalog)
    return GameService(
        config,
        catalog,
        repository,
        engine,
        Planner(catalog),
        Presenter(catalog, engine),
        reply_service,
        search_free=reply_service.search_free,
    )


def get_game_service(request: Request) -> GameService:
    """앱 기동 시 구성한 수사 서비스를 제공한다.

    Args:
        request: 실행 중인 FastAPI 앱에 접근하는 요청.

    Returns:
        GameService: 현재 앱의 수사 처리 서비스.
    """
    return request.app.state.service
