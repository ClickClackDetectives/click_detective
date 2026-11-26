"""획득 자료, 쟁점과 증거 자산 API."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

from app.investigation.controllers.investigation_request_context import game
from app.investigation.providers.investigation_provider import get_game_service
from app.investigation.repositories.investigation_evidence_image_repository import (
    evidence_image_path,
)
from app.runtime.runtime_auth import authenticate

router = APIRouter(dependencies=[Depends(authenticate)])


@router.get("/v1/games/{game_id}/materials", tags=["자료"])
def materials(
    game_id: str,
    request: Request,
    kind: str | None = None,
    archive_kind: str | None = None,
    search: str = "",
    place: str | None = None,
):
    """공개 가능한 목록을 백엔드에서 분류·검색한다. GET은 열람 처리하지 않는다.

    Args:
        game_id (str): 조회하거나 변경할 수사의 식별자.
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
        kind (str | None): 조회할 자료 종류.
        archive_kind (str | None): 자료실 분류 조건. 생략하면 모든 분류를 포함한다.
        search (str): 목록에서 찾을 검색 문자열.
        place (str | None): 조회할 장소 이름 또는 all.

    Returns:
        dict: 분류·장소·검색 조건에 맞는 자료 목록.
    """
    rows = get_game_service(request).presenter.materials(game(request, game_id))
    selected_materials = []
    for material in rows:
        if kind and material["kind"] != kind:
            continue
        if archive_kind and material["archiveKind"] != archive_kind:
            continue
        if place and material.get("type") != place:
            continue
        words = []
        for field in ["code", "title", "summary", "type"]:
            words.append(str(material.get(field, "")))
        searchable_text = " ".join(words).casefold()
        if search.casefold() in searchable_text:
            selected_materials.append(material)
    return {"materials": selected_materials}


@router.get("/v1/games/{game_id}/materials/{material_key}", tags=["자료"])
def material_detail(game_id: str, material_key: str, request: Request):
    """획득한 원본·진술·추론만 본문을 제공한다. 접두사로 ID 충돌을 구분한다.

    Args:
        game_id (str): 조회하거나 변경할 수사의 식별자.
        material_key (str): 자료 종류와 ID를 합친 키. 예: evidence:1-01.
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

    Returns:
        dict: 열람 가능한 원본 자료 또는 획득한 진술·추론의 상세 정보.
    """
    state = game(request, game_id)
    kind, separator, key = material_key.partition(":")
    if not separator or kind not in {"evidence", "testimony", "derived"}:
        raise HTTPException(422, "자료 키를 확인하세요.")
    game_service = get_game_service(request)
    game_service.engine.readable_source(state, {"kind": kind, "id": key})
    if kind == "evidence":
        record = game_service.catalog.evidence[key]
        return {
            "kind": kind,
            **{
                field: record[field]
                for field in ("id", "code", "title", "type", "time", "phase", "body")
            },
            "illustration": (
                f"/v1/games/{game_id}/evidence-assets/{key}"
                if evidence_image_path(game_service.catalog, key)
                else None
            ),
        }
    return {
        "kind": kind,
        **state["statements" if kind == "testimony" else "derivedEvidence"][key],
    }


@router.get("/v1/games/{game_id}/evidence-assets/{evidence_id}", tags=["자산"])
def evidence_asset(game_id: str, evidence_id: str, request: Request):
    """원본 자료의 이미지도 열람 조건을 확인한다. 사용자 파일 경로는 받지 않는다.

    Args:
        game_id (str): 조회하거나 변경할 수사의 식별자.
        evidence_id (str): 원본 증거의 식별자.
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

    Returns:
        FileResponse: 획득 조건과 경로를 검사한 증거 이미지 응답.
    """
    state = game(request, game_id)
    game_service = get_game_service(request)
    game_service.engine.readable_source(state, {"kind": "evidence", "id": evidence_id})
    path = evidence_image_path(game_service.catalog, evidence_id)
    if path is None:
        raise HTTPException(404, "이미지를 찾을 수 없습니다.")
    return FileResponse(path)


@router.get("/v1/games/{game_id}/findings", tags=["쟁점"])
def findings(game_id: str, request: Request):
    """이미 발견된 쟁점만 반환한다. 미발견 조건·정답 목록은 공개하지 않는다.

    Args:
        game_id (str): 조회하거나 변경할 수사의 식별자.
        request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

    Returns:
        dict: 이미 발견한 쟁점 목록을 담은 findings 항목.
    """
    return {"findings": game(request, game_id)["findingDetails"]}
