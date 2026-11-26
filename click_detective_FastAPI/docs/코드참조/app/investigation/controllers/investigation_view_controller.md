# `app/investigation/controllers/investigation_view_controller.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/controllers/investigation_view_controller.py)

수사 화면별 검색 API.

## `screen_view`

[소스 선언](../../../../../app/investigation/controllers/investigation_view_controller.py#L14)

```python
def screen_view(game_id: str, screen: str, request: Request, search: str='', place: str='all', person: str='all', category: str='evidence'):
    ...
```

원본 Next.js 화면의 분류·검색을 서버에서 처리하고 표시 결과만 돌려준다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- screen (str): 조회할 화면 이름.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
- search (str): 목록에서 찾을 검색 문자열.
- place (str): 조회할 장소 이름 또는 all.
- person (str): 조회할 인물 식별자 또는 all.
- category (str): 조회할 자료 분류.

**반환값**

- dict: 선택한 수사 화면의 검색·분류 결과.
