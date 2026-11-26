"""사건과 공개 자산 API."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from ...runtime.runtime_auth import authenticate
from ..providers.cases_provider import get_catalog_service
from ..services.cases_catalog_service import CatalogService

CatalogDependency = Annotated[CatalogService, Depends(get_catalog_service)]

router = APIRouter(dependencies=[Depends(authenticate)])


@router.get("/v1/catalog", tags=["사건"])
async def catalog(catalog_service: CatalogDependency):
    """초기 화면 데이터 전체를 공개 DTO로 반환한다.

    Args:
        catalog_service: 공개 사건과 자산을 조회할 카탈로그 서비스.

    Returns:
        dict: 초기 화면에 사용할 공개 사건·인물·자료 정보.
    """
    return catalog_service.public_catalog()


@router.get("/v1/cases", tags=["사건"])
async def cases(catalog_service: CatalogDependency):
    """실제로 시작 가능한 사건만 반환한다.

    Args:
        catalog_service: 공개 사건과 자산을 조회할 카탈로그 서비스.

    Returns:
        dict: 시작할 수 있는 사건 ID, 버전과 소개의 목록.
    """
    return catalog_service.list_cases()


@router.get("/v1/cases/{case_id}", tags=["사건"])
async def case_detail(case_id: str, catalog_service: CatalogDependency):
    """사건 소개·인물·공개 콘텐츠를 반환한다. 비공개 규칙은 제외한다.

    Args:
        case_id (str): 조회하거나 생성할 사건의 식별자.
        catalog_service: 공개 사건과 자산을 조회할 카탈로그 서비스.

    Returns:
        dict: 지정 사건의 공개 카탈로그.
    """
    return catalog_service.case_detail(case_id)


@router.get("/v1/assets/{asset_path:path}", tags=["자산"])
async def public_asset(asset_path: str, catalog_service: CatalogDependency):
    """소개·인물 이미지·영상만 제공한다. 증거 이미지는 수사 권한 경로로 제공한다.

    Args:
        asset_path (str): 공개 자산의 상대 경로.
        catalog_service: 공개 사건과 자산을 조회할 카탈로그 서비스.

    Returns:
        FileResponse: 공개 자산 파일의 HTTP 응답.
    """
    return FileResponse(catalog_service.public_asset(asset_path))
