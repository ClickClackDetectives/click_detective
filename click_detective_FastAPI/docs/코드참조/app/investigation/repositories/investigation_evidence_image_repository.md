# `app/investigation/repositories/investigation_evidence_image_repository.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/repositories/investigation_evidence_image_repository.py)

원본 경로 또는 증거 ID로 추가한 참고 이미지 파일을 찾는다.

## `evidence_image_path`

[소스 선언](../../../../../app/investigation/repositories/investigation_evidence_image_repository.py#L8)

```python
def evidence_image_path(catalog: Catalog, evidence_id: str) -> Path | None:
    ...
```

기존 사건 버전을 바꾸지 않고 추가한 증거 이미지도 찾는다.

**인자**

- catalog (Catalog): 자료 목록과 정적 파일 루트를 가진 사건 카탈로그.
- evidence_id (str): 열람 권한을 확인한 원본 증거의 식별자.

**반환값**

- Path | None: public 내부의 실제 이미지 파일. 없거나 외부 경로면 None.
