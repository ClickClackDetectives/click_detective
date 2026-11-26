"""대화 그래프와 앱 수명 동안 사용하는 검색 인덱스를 조립한다."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Request

from app.cases.repositories.cases_file_repository import Catalog
from app.dialogue.services.reply.dialogue_interrogation_graph import InterrogationGraph
from app.dialogue.services.reply.dialogue_reply_service import ReplyService
from app.runtime.runtime_settings import PROJECT_ROOT, Settings


@asynccontextmanager
async def open_reply_service(
    config: Settings, catalog: Catalog
) -> AsyncIterator[ReplyService]:
    """설정에 따라 검색기와 로컬 모델을 준비하고 검색 인덱스를 정리한다.

    Args:
        config: 모델 실행 모드와 검색 설정.
        catalog: 검색기에서 공개할 수 있는 사건 데이터를 조회하는 저장소.

    Returns:
        AsyncIterator[ReplyService]: 앱 실행 중 사용하는 대화 서비스.
    """
    model = None
    question_search = None
    index = None
    embedding_dir = config.rag_embedding_dir
    if config.generation_mode == "local":
        embedding_dir = embedding_dir or PROJECT_ROOT / "models/retrieval"
    try:
        if config.rag_enabled and embedding_dir is not None:
            from app.dialogue.repositories.dialogue_chroma_index import ChromaIndex
            from app.dialogue.services.preprocess_agent.rag.dialogue_embeddings import (
                E5Encoder,
            )
            from app.dialogue.services.preprocess_agent.rag.dialogue_fact_retriever import (
                QuestionSearch,
            )

            encoder = await asyncio.to_thread(E5Encoder, embedding_dir)
            index = await asyncio.to_thread(ChromaIndex, encoder)
            reranker = None
            if config.rag_bm25_enabled:
                from app.dialogue.services.preprocess_agent.rag.dialogue_kiwi_reranker import (
                    KiwiBM25Reranker,
                )

                reranker = await asyncio.to_thread(
                    KiwiBM25Reranker, config.rag_dense_weight, config.rag_rrf_k
                )
            question_search = QuestionSearch(catalog, config, index, reranker)
        if config.generation_mode == "local":
            from app.dialogue.services.model.dialogue_local_model import LocalQwenModel

            model = LocalQwenModel(config)
            await asyncio.to_thread(model.load)
        graph = InterrogationGraph(config, model, question_search)
        yield ReplyService(config, graph, search_free=question_search is not None)
    finally:
        if index is not None:
            await asyncio.to_thread(index.close)


def get_reply_service(request: Request) -> ReplyService:
    """앱 기동 시 구성한 대화 서비스를 제공한다.

    Args:
        request: 실행 중인 FastAPI 앱에 접근하는 요청.

    Returns:
        ReplyService: 현재 앱의 대화 처리 서비스.
    """
    return request.app.state.reply_service
