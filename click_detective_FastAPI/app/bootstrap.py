"""서버가 시작될 때 사건, 수사 서비스와 대화 모델을 준비한다."""

import asyncio
from contextlib import asynccontextmanager

from app.investigation.persistence.mongo_repository import MongoRepository
from app.investigation.rules.engine import Engine
from app.investigation.views.presentation import Presenter

from .cases.catalog import Catalog
from .config import PROJECT_ROOT, Settings
from .dialogue.interrogation_graph import InterrogationGraph
from .dialogue.preprocess_agent.planning import Planner
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
    model = None
    question_search = None
    index = None
    repository = None
    auth = None
    embedding_dir = config.rag_embedding_dir
    if config.generation_mode == "local":
        embedding_dir = embedding_dir or PROJECT_ROOT / "models/retrieval"
    try:
        if config.mongo_uri is None:
            raise RuntimeError("수사를 저장할 CLICK_MONGO_URI를 설정하세요.")
        repository = await asyncio.to_thread(
            MongoRepository, config.mongo_uri.get_secret_value(), config.mongo_database
        )
        if config.postgres_dsn is not None:
            from .auth.service import AuthService

            auth = await asyncio.to_thread(
                AuthService,
                config.postgres_dsn.get_secret_value(),
                config.auth_jwt_secret.get_secret_value(),
            )
        if config.rag_enabled and embedding_dir is not None:
            from .dialogue.preprocess_agent.chroma_index import ChromaIndex
            from .dialogue.preprocess_agent.embeddings import E5Encoder
            from .dialogue.preprocess_agent.question_search import QuestionSearch

            encoder = await asyncio.to_thread(E5Encoder, embedding_dir)
            index = await asyncio.to_thread(ChromaIndex, encoder)
            reranker = None
            if config.rag_bm25_enabled:
                from .dialogue.preprocess_agent.kiwi_reranker import KiwiBM25Reranker

                reranker = await asyncio.to_thread(
                    KiwiBM25Reranker, config.rag_dense_weight, config.rag_rrf_k
                )
            question_search = QuestionSearch(catalog, config, index, reranker)
        if config.generation_mode == "local":
            from .dialogue.local_model import LocalQwenModel

            model = LocalQwenModel(config)
            await asyncio.to_thread(model.load)
        service = GameService(
            config,
            catalog,
            repository,
            engine,
            Planner(catalog),
            presenter,
            InterrogationGraph(config, model, question_search),
            search_free=question_search is not None,
        )
        app.state.settings = config
        app.state.service = service
        app.state.auth = auth
        yield
    finally:
        if auth is not None:
            await asyncio.to_thread(auth.close)
        if repository is not None:
            await asyncio.to_thread(repository.close)
        if index is not None:
            await asyncio.to_thread(index.close)
