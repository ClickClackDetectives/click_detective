"""사건 저장소와 카탈로그 서비스의 앱 수명 의존성을 제공한다."""

from pathlib import Path

from fastapi import Request

from ..repositories.cases_file_repository import Catalog
from ..services.cases_catalog_service import CatalogService


def build_catalog_service(data_dir: Path) -> CatalogService:
    """사건 파일을 확인하고 카탈로그 서비스를 조립한다.

    Args:
        data_dir: 매니페스트와 사건 데이터가 있는 디렉터리.

    Returns:
        CatalogService: 기동 시 초기화한 사건 파일 저장소를 사용하는 서비스.
    """
    repository = Catalog(data_dir)
    return CatalogService(repository)


async def get_catalog_service(request: Request) -> CatalogService:
    """현재 앱의 카탈로그 서비스를 HTTP 컨트롤러에 주입한다.

    Args:
        request: 시작 시 구성한 앱에 접근할 수 있는 HTTP 요청.

    Returns:
        CatalogService: 요청을 받은 앱이 보관하는 공개 카탈로그 서비스.
    """
    return request.app.state.catalog_service
