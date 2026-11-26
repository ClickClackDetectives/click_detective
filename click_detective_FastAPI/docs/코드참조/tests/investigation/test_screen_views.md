# `tests/investigation/test_screen_views.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/investigation/test_screen_views.py)

원본 Next.js 화면용 조회 계약이 비공개 본문을 유출하지 않고 같은 분류를 제공하는지 검사한다.

## `test_original_ui_catalog_and_views`

[소스 선언](../../../../tests/investigation/test_screen_views.py#L6)

```python
def test_original_ui_catalog_and_views(api, game):
    ...
```

공개 카탈로그·집사 분류·서버 검색·집계·권한·본문 읽기 순서를 확인한다.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
