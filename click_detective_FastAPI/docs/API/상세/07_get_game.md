# 07. 수사 복원과 화면 상태 집계

`GET /v1/games/{game_id}`

이미 만든 수사의 현재 상태를 복원한다. 이어하기에서는 이 응답의 revision을 사용한다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 익명 수사는 `X-Game-Token`, 계정 수사는 `X-Access-Token`과 해당 계정 문맥으로 접근한다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

## 서버 처리 순서

1. 게임 ID와 게임 토큰으로 소유권을 확인합니다.
2. 수사의 고정 시나리오 버전이 현재와 같은지 확인합니다.
3. Presenter가 자료 목록·진행률·타임라인·행동 가능 여부를 계산합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

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

처리 진입점은 `get_game()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_game_controller.py#L43)
