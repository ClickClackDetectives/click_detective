"""원본 경로 또는 증거 ID로 추가한 참고 이미지 파일을 찾는다."""

from pathlib import Path

from app.cases.catalog import Catalog


def evidence_image_path(catalog: Catalog, evidence_id: str) -> Path | None:
    """기존 사건 버전을 바꾸지 않고 추가한 증거 이미지도 찾는다.

    Args:
        catalog (Catalog): 자료 목록과 정적 파일 루트를 가진 사건 카탈로그.
        evidence_id (str): 열람 권한을 확인한 원본 증거의 식별자.

    Returns:
        Path | None: public 내부의 실제 이미지 파일. 없거나 외부 경로면 None.
    """
    record = catalog.evidence[evidence_id]
    name = record.get("illustration") or f"assets/evidence/{evidence_id}.png"
    public = (catalog.root / "public").resolve()
    path = (public / name.lstrip("/")).resolve()
    if not path.is_relative_to(public) or not path.is_file():
        return None
    return path
