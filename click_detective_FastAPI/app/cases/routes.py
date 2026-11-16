"""사건과 공개 자산 API."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse

from ..dependencies import authenticate, service

router = APIRouter(dependencies=[Depends(authenticate)])


@router.get("/v1/catalog", tags=["사건"])
async def catalog(request: Request):
    """초기 화면 데이터 전체를 공개 DTO로 반환한다.

    Args:
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

    Returns:
        dict: 초기 화면에 사용할 공개 사건·인물·자료 정보.
    """
    return service(request).catalog.public_catalog()


@router.get("/v1/cases", tags=["사건"])
async def cases(request: Request):
    """실제로 시작 가능한 사건만 반환한다.

    Args:
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

    Returns:
        dict: 시작할 수 있는 사건 ID, 버전과 소개의 목록.
    """
    data = service(request).catalog
    return {
        "cases": [
            {
                "case_id": data.case_id,
                "scenario_version": data.version,
                **data.case["case"],
            }
        ]
    }


@router.get("/v1/cases/{case_id}", tags=["사건"])
async def case_detail(case_id: str, request: Request):
    """사건 소개·인물·공개 콘텐츠를 반환한다. 비공개 규칙은 제외한다.

    Args:
        case_id (str): 조회하거나 생성할 사건의 식별자.
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

    Returns:
        dict: 지정 사건의 공개 카탈로그.
    """
    service(request).catalog.require_case(case_id)
    return service(request).catalog.public_catalog()


@router.get("/v1/assets/{asset_path:path}", tags=["자산"])
async def public_asset(asset_path: str, request: Request):
    """소개·인물 이미지·영상만 제공한다. 증거 이미지는 수사 권한 경로로 제공한다.

    Args:
        asset_path (str): 공개 자산의 상대 경로.
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

    Returns:
        FileResponse: 공개 자산 파일의 HTTP 응답.
    """
    return FileResponse(service(request).catalog.public_asset(asset_path))
