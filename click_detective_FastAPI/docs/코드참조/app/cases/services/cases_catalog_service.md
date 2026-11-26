# `app/cases/services/cases_catalog_service.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/cases/services/cases_catalog_service.py)

사건 조회와 공개 카탈로그 조립을 담당한다.

## `CatalogService`

[소스 선언](../../../../../app/cases/services/cases_catalog_service.py#L10)

```python
class CatalogService:
    ...
```

사건 저장소의 데이터로 공개 API 응답을 조립한다.

**인자**

- repository: 기동 시 무결성을 확인한 사건 파일 저장소.

**반환값**

- CatalogService: 공개 사건 목록과 카탈로그를 제공하는 서비스.

## `CatalogService.__init__`

[소스 선언](../../../../../app/cases/services/cases_catalog_service.py#L20)

```python
def __init__(self, repository: Catalog):
    ...
```

공개 응답을 조립할 사건 파일 저장소를 보관한다.

**인자**

- repository: 기동 시 무결성을 확인한 사건 파일 저장소.

**반환값**

- None: 반환값 없음.

## `CatalogService.list_cases`

[소스 선언](../../../../../app/cases/services/cases_catalog_service.py#L31)

```python
def list_cases(self) -> dict:
    ...
```

현재 시작할 수 있는 사건의 소개와 버전을 반환한다.

**인자**

- 없음.

**반환값**

- dict: 시작 가능한 사건을 cases 목록에 담은 응답.

## `CatalogService.case_detail`

[소스 선언](../../../../../app/cases/services/cases_catalog_service.py#L51)

```python
def case_detail(self, case_id: str) -> PublicCatalog:
    ...
```

사건 ID를 확인하고 해당 사건의 공개 카탈로그를 반환한다.

**인자**

- case_id: 조회할 사건의 식별자.

**반환값**

- PublicCatalog: 사건 소개와 화면에 공개되는 정보.

**예외**

- HTTPException: 현재 시작 가능한 사건의 ID와 다르면 404가 발생한다.

## `CatalogService.public_asset`

[소스 선언](../../../../../app/cases/services/cases_catalog_service.py#L66)

```python
def public_asset(self, asset_path: str) -> Path:
    ...
```

공개 자산 요청에 사용할 파일 경로를 반환한다.

**인자**

- asset_path: 공개 디렉터리 기준 상대 경로.

**반환값**

- Path: 공개 여부와 존재를 확인한 실제 파일 경로.

**예외**

- HTTPException: 공개 대상이 아니거나 파일이 없으면 404가 발생한다.

## `CatalogService.public_catalog`

[소스 선언](../../../../../app/cases/services/cases_catalog_service.py#L80)

```python
def public_catalog(self) -> PublicCatalog:
    ...
```

초기 화면 콘텐츠·인물·선택지만 명시적으로 공개한다. 규칙 원문은 제외한다.

**인자**

- 없음.

**반환값**

- dict: 공개가 허용된 사건·인물·자료 목록과 화면 설정.
