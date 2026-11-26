# 15. 조건을 충족한 2차 조사 시작

`POST /v1/games/{game_id}/phase-transitions`

서버가 정한 전환 조건을 충족했을 때 다음 조사 단계로 진행한다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 익명 수사는 `X-Game-Token`, 계정 수사는 `X-Access-Token`과 해당 계정 문맥으로 접근한다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

| 필드 | 자료형 | 기본/필수 | 의미 |
| --- | --- | --- | --- |
| request_id | UUID | 필수 | 행동마다 새 UUID, 같은 행동 재전송만 유지 |
| expected_revision | 0 이상 정수 | 필수 | 최신 state.revision |
| target_phase | 정수 | 2 | 2만 허용 |

예시의 UUID는 새로 생성하고, revision과 ID는 현재 수사 응답에서 가져온다.

```json
{
  "request_id": "0000000f-1111-4111-8111-111111111111",
  "expected_revision": 0,
  "target_phase": 2
}
```

## 서버 처리 순서

1. 현재 1차인지 검사합니다.
2. 추론 2개·쟁점 2개 이상 조건을 확인합니다.
3. phase=2와 자동 원본 2-03 열람을 같이 확정합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

```json
{
  "request_id": "이번 요청 UUID",
  "result": {
    "phase": 2
  },
  "state": {
    "id": "수사 UUID",
    "revision": 1
  }
}
```

## 실패·주의점

- 409: 이미 2차 또는 종결.
- 422: 조건 미충족. target_phase는 2만 허용합니다.

처리 진입점은 `advance()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_game_controller.py#L102)
