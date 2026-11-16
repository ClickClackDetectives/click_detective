# `tests/investigation/test_api_routes.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/investigation/test_api_routes.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 41줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

investigation/test_api_routes.py의 회귀 동작을 확인한다.

## `test_all_business_routes_have_coverage`

[소스 선언 위치](../../../../tests/investigation/test_api_routes.py#L4)

```python
def test_all_business_routes_have_coverage(api):
    ...
```

새 API가 생기면 검사 목록을 함께 갱신하도록 OpenAPI 경로를 확인한다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
