# `app/cases/controllers/cases_controller.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/cases/controllers/cases_controller.py)

사건과 공개 자산 API.

## `catalog`

[소스 선언](../../../../../app/cases/controllers/cases_controller.py#L18)

```python
async def catalog(catalog_service: CatalogDependency):
    ...
```

초기 화면 데이터 전체를 공개 DTO로 반환한다.

**인자**

- catalog_service: 공개 사건과 자산을 조회할 카탈로그 서비스.

**반환값**

- dict: 초기 화면에 사용할 공개 사건·인물·자료 정보.

## `cases`

[소스 선언](../../../../../app/cases/controllers/cases_controller.py#L31)

```python
async def cases(catalog_service: CatalogDependency):
    ...
```

실제로 시작 가능한 사건만 반환한다.

**인자**

- catalog_service: 공개 사건과 자산을 조회할 카탈로그 서비스.

**반환값**

- dict: 시작할 수 있는 사건 ID, 버전과 소개의 목록.

## `case_detail`

[소스 선언](../../../../../app/cases/controllers/cases_controller.py#L44)

```python
async def case_detail(case_id: str, catalog_service: CatalogDependency):
    ...
```

사건 소개·인물·공개 콘텐츠를 반환한다. 비공개 규칙은 제외한다.

**인자**

- case_id (str): 조회하거나 생성할 사건의 식별자.
- catalog_service: 공개 사건과 자산을 조회할 카탈로그 서비스.

**반환값**

- dict: 지정 사건의 공개 카탈로그.

## `public_asset`

[소스 선언](../../../../../app/cases/controllers/cases_controller.py#L58)

```python
async def public_asset(asset_path: str, catalog_service: CatalogDependency):
    ...
```

소개·인물 이미지·영상만 제공한다. 증거 이미지는 수사 권한 경로로 제공한다.

**인자**

- asset_path (str): 공개 자산의 상대 경로.
- catalog_service: 공개 사건과 자산을 조회할 카탈로그 서비스.

**반환값**

- FileResponse: 공개 자산 파일의 HTTP 응답.
