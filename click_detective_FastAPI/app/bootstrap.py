"""서버가 시작될 때 사건, 수사 서비스와 대화 모델을 준비한다."""

import asyncio
from contextlib import asynccontextmanager

from .cases.catalog import Catalog
from .config import Settings
from .dialogue.preprocess_agent.planning import Planner
from .investigation.engine import Engine
from .investigation.presentation import Presenter
from .investigation.repository import Repository
from .investigation.service import GameService


@asynccontextmanager
async def lifespan(app):
    """정적 데이터와 모델은 한 번 로딩한다. fixture 모드에서만 GPU를 생략한다.

    Args:
        app: 설정과 서비스를 보관할 FastAPI 애플리케이션.

    Returns:
        AsyncIterator[None]: 앱의 시작 준비를 끝낸 뒤 실행을 서버에 넘기는 비동기 반복자.
    """
    if app.state.initial_settings is None:
        config = Settings()
    else:
        config = app.state.initial_settings
    catalog = Catalog(config.data_dir)
    engine = Engine(catalog)
    presenter = Presenter(catalog, engine)
    graph = None
    if config.generation_mode == "local":
        from .dialogue.interrogation_graph import InterrogationGraph
        from .dialogue.local_model import LocalQwenModel

        model = LocalQwenModel(config)
        await asyncio.to_thread(model.load)
        graph = InterrogationGraph(config, model)
    service = GameService(
        config,
        catalog,
        Repository(config.database_path),
        engine,
        Planner(catalog),
        presenter,
        graph,
    )
    app.state.settings = config
    app.state.service = service
    yield
