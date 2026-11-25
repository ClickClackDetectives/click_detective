# 07. 수사 복원과 화면 상태 집계

[API 목차](README.md) · [공통 규칙](../공통규칙.md)

## 역할과 호출 시점

`GET /v1/games/{game_id}`

수사 복원과 화면 상태 집계에 사용하는 실제 구현 경로입니다. 공개 상태나 파일을 조회합니다. GET은 게임 상태를 변경하지 않습니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다. 수사별 `X-Game-Token: <생성 응답의 game_token>`도 필요합니다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

## 서버 처리 순서

1. 게임 ID와 게임 토큰으로 소유권을 확인합니다.
2. 수사의 고정 시나리오 버전이 현재와 같은지 확인합니다.
3. Presenter가 자료 목록·진행률·타임라인·행동 가능 여부를 계산합니다.

## 응답

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

```json
{
  "state": {
    "id": "수사 UUID",
    "revision": 0,
    "phase": 1,
    "progress": {
      "percent": 0
    },
    "availableActions": {}
  }
}
```

## 실패·주의점

- 404: 수사 또는 토큰 불일치.
- 409: 시나리오 버전 충돌.
- GET은 질문이나 열람을 변경하지 않습니다.
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

현재 API 진입점은 [app/investigation/api/routes.py의 `get_game`](../../../app/investigation/api/routes.py#L26)다.

처리 순서는 [GameService](../../코드참조/app/investigation/service.md), 저장 조건은 [수사 저장](../../서버/수사_저장.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/views/presentation.md)에서 확인한다.
