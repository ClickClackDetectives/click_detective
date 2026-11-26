# `app/cases/dto/cases_catalog_dto.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/cases/dto/cases_catalog_dto.py)

공개 카탈로그의 응답 키와 자료 구조를 정의한다.

## `PublicCatalog`

[소스 선언](../../../../../app/cases/dto/cases_catalog_dto.py#L6)

```python
class PublicCatalog(TypedDict):
    ...
```

소개 화면과 수사 시작 화면에서 읽는 공개 카탈로그를 정의한다.

**인자**

- 없음.

**반환값**

- PublicCatalog: 사건과 인물의 공개 정보 및 화면 설정을 담은 사전.
