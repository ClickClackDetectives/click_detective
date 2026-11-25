"""FastAPI 검사에 사용할 격리 MongoDB 설정을 제공한다."""

import os
from uuid import uuid4

import pytest
from pymongo import MongoClient

from app.config import Settings


@pytest.fixture(scope="session")
def fixture_settings(tmp_path_factory, service_key):
    """GPU 없이 실행할 FastAPI 테스트 설정을 구성한다.

    Args:
        tmp_path_factory: 진단용 임시 디렉터리를 만드는 도구.
        service_key: 테스트 요청과 예제에 사용하는 서버 인증 키.

    Returns:
        Settings: 임시 MongoDB를 사용하는 fixture 설정을 제공하는 반복자.
    """
    uri = os.getenv("CLICK_TEST_MONGO_URI")
    if not uri:
        pytest.skip("CLICK_TEST_MONGO_URI가 필요합니다.")
    database = f"click_fixture_{uuid4().hex}"
    settings = Settings(
        api_key=service_key,
        generation_mode="fixture",
        validation_similarity_backend="char_ngram",
        fallback_on_error=False,
        _env_file=None,
        mongo_uri=uri,
        mongo_database=database,
        postgres_dsn=None,
        auth_jwt_secret=None,
        diagnostics_path=tmp_path_factory.mktemp("click-traces") / "trace.jsonl",
    )

    try:
        yield settings
    finally:
        with MongoClient(uri) as mongo:
            for collection in mongo[database].list_collection_names():
                mongo[database].drop_collection(collection)
