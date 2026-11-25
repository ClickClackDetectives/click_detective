"""삭제 대기 계정의 수사와 세션을 정리한다."""

import argparse
from contextlib import ExitStack

from app.auth.deletion import process_one
from app.auth.repository import AuthRepository
from app.config import Settings
from app.investigation.persistence.mongo_repository import MongoRepository


def main():
    """설정한 두 저장소를 열고 실행 가능한 삭제 작업을 처리한다.

    Args:
        없음.

    Returns:
        None: 실행한 작업의 개수를 출력한다.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limit", type=int, default=100, help="한 번에 처리할 최대 작업 수"
    )
    options = parser.parse_args()
    if not 1 <= options.limit <= 1000:
        parser.error("--limit에 1부터 1000 사이의 정수를 입력하세요.")
    settings = Settings()
    if settings.postgres_dsn is None or settings.mongo_uri is None:
        parser.error("계정과 수사 저장소 연결을 모두 설정하세요.")
    with ExitStack() as resources:
        auth_repository = AuthRepository(settings.postgres_dsn.get_secret_value())
        resources.callback(auth_repository.close)
        investigations = MongoRepository(
            settings.mongo_uri.get_secret_value(), settings.mongo_database
        )
        resources.callback(investigations.close)
        completed = 0
        while completed < options.limit:
            if not process_one(auth_repository, investigations.delete_owned):
                break
            completed += 1
    print(f"완료한 계정 삭제 작업: {completed}")


if __name__ == "__main__":
    main()
