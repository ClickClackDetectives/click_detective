# 08. 자료 목록·서버 필터·검색

[API 목차](README.md) · [공통 규칙](../공통규칙.md)

## 역할과 호출 시점

`GET /v1/games/{game_id}/materials`

자료 목록·서버 필터·검색에 사용하는 실제 구현 경로입니다. 공개 상태나 파일을 조회합니다. GET은 게임 상태를 변경하지 않습니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다. 수사별 `X-Game-Token: <생성 응답의 game_token>`도 필요합니다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

쿼리: kind=evidence/testimony/derived, archive_kind=evidence/testimony/inference, search=검색어, place=장소 이름. 필터는 선택적이며 단순 대소문자 무시 문자열 포함 검색입니다. 잘못된 종류 문자열을 별도 enum 오류로 거절하지 않고 빈 목록이 될 수 있습니다.

## 서버 처리 순서

1. 현재 phase에 공개 가능한 원본 제목·요약을 구성합니다.
2. 기록된 진술과 생성된 추론도 같은 목록에 합칩니다.
3. kind·archive_kind·search·place로 서버에서 필터링합니다.

## 응답

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

```json
{
  "materials": [
    {
      "id": "1-01",
      "kind": "evidence",
      "archiveKind": "evidence",
      "acquired": false,
      "materialKey": "evidence:1-01",
      "title": "자료 제목"
    }
  ]
}
```

## 실패·주의점

- 필터는 일반 문자열이며 알 수 없는 값은 보통 빈 목록입니다.
- 목록이 보인다고 본문을 열람한 것은 아닙니다.
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

현재 API 진입점은 [app/investigation/material_routes.py의 `materials`](../../../app/investigation/material_routes.py#L12)다.

처리 순서는 [GameService](../../코드참조/app/investigation/service.md), 저장 조건은 [Repository](../../코드참조/app/investigation/repository.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/presentation.md)에서 확인한다.
