"""이미지 없는 자료와 나중에 추가한 증거 이미지를 검사한다."""

from types import SimpleNamespace

from app.investigation.repositories.investigation_evidence_image_repository import (
    evidence_image_path,
)


def test_optional_image_path_and_public_boundary(tmp_path):
    """null 경로·추가 이미지·public 밖 경로를 확인한다.

    Args:
        tmp_path: 이미지 파일을 만드는 검사 전용 임시 폴더.

    Returns:
        None: 경로 선택과 외부 파일 차단 결과를 검사한다.
    """
    catalog = SimpleNamespace(root=tmp_path, evidence={"2-01": {"illustration": None}})
    assert evidence_image_path(catalog, "2-01") is None
    image = tmp_path / "public/assets/evidence/2-01.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"test image")
    assert evidence_image_path(catalog, "2-01") == image
    outside = tmp_path / "secret.png"
    outside.write_bytes(b"private")
    catalog.evidence["2-01"]["illustration"] = "../secret.png"
    assert evidence_image_path(catalog, "2-01") is None


def test_missing_image_is_null_in_detail_and_404_in_asset(api, play, monkeypatch):
    """이미지 없는 자료를 열어도 서버 오류나 잘못된 이미지 주소가 나오지 않는다.

    Args:
        api: 인증된 API 요청을 보내는 검사 함수.
        play: 사용자 행동으로 수사를 진행하는 검사 도우미.
        monkeypatch: 이미지 없는 상태를 재현하는 pytest 도우미.

    Returns:
        None: 상세 응답과 이미지 API의 상태 코드를 확인한다.
    """
    monkeypatch.setattr(
        "app.investigation.controllers.investigation_material_controller.evidence_image_path",
        lambda *args: None,
    )
    play.act("examinations", evidence_id="1-01")
    base = f"/v1/games/{play.game_id}"
    detail = api("GET", base + "/materials/evidence:1-01", game_token=play.token)
    assert detail.status_code == 200
    assert detail.json()["illustration"] is None
    image = api("GET", base + "/evidence-assets/1-01", game_token=play.token)
    assert image.status_code == 404


def test_second_phase_image_requires_ownership_and_examination(api, play):
    """추가 이미지가 있어도 다음 단계·미열람 자료의 접근 권한은 유지한다.

    Args:
        api: 인증된 API 요청을 보내는 검사 함수.
        play: 현재 수사와 접근 토큰을 보관하는 검사 도우미.

    Returns:
        None: 공개 자산과 미획득 이미지 요청이 차단되는지 확인한다.
    """
    path = f"/v1/games/{play.game_id}/evidence-assets/2-01"
    assert api("GET", path).status_code == 404
    assert api("GET", path, game_token=play.token).status_code == 422
    assert api("GET", "/v1/assets/assets/evidence/2-01.png").status_code == 404
