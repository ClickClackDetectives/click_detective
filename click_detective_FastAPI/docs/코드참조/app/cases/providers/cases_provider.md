# `app/cases/providers/cases_provider.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/cases/providers/cases_provider.py)

사건 저장소와 카탈로그 서비스의 앱 수명 의존성을 제공한다.

## `build_catalog_service`

[소스 선언](../../../../../app/cases/providers/cases_provider.py#L11)

```python
def build_catalog_service(data_dir: Path) -> CatalogService:
    ...
```

사건 파일을 확인하고 카탈로그 서비스를 조립한다.

**인자**

- data_dir: 매니페스트와 사건 데이터가 있는 디렉터리.

**반환값**

- CatalogService: 기동 시 초기화한 사건 파일 저장소를 사용하는 서비스.

## `get_catalog_service`

[소스 선언](../../../../../app/cases/providers/cases_provider.py#L24)

```python
async def get_catalog_service(request: Request) -> CatalogService:
    ...
```

현재 앱의 카탈로그 서비스를 HTTP 컨트롤러에 주입한다.

**인자**

- request: 시작 시 구성한 앱에 접근할 수 있는 HTTP 요청.

**반환값**

- CatalogService: 요청을 받은 앱이 보관하는 공개 카탈로그 서비스.
