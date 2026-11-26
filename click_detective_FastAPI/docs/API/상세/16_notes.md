# 16. 메모 전체 저장

`PUT /v1/games/{game_id}/notes`

수사 메모를 받은 문자열 전체로 교체한다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 익명 수사는 `X-Game-Token`, 계정 수사는 `X-Access-Token`과 해당 계정 문맥으로 접근한다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

| 필드 | 자료형 | 기본/필수 | 의미 |
| --- | --- | --- | --- |
| request_id | UUID | 필수 | 행동마다 새 UUID, 같은 행동 재전송만 유지 |
| expected_revision | 0 이상 정수 | 필수 | 최신 state.revision |
| text | 문자열 | 필수 | 0~20000자, 전체 교체 |

예시의 UUID는 새로 생성하고, revision과 ID는 현재 수사 응답에서 가져온다.

```json
{
  "request_id": "00000010-1111-4111-8111-111111111111",
  "expected_revision": 0,
  "text": "확인한 자료와 진술을 비교할 것."
}
```

## 서버 처리 순서

1. 문자열 길이·revision·종결 여부를 확인합니다.
2. state.notes를 전체 text로 교체합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

```json
{
  "request_id": "이번 요청 UUID",
  "result": {
    "saved": true
  },
  "state": {
    "id": "수사 UUID",
    "revision": 1
  }
}
```

## 실패·주의점

- 422: 20,000자 초과 또는 잘못된 형식.
- 409: 오래된 revision·종결.
- 메모도 공식 상태의 revision을 공유하므로 생성 중 충돌이 생길 수 있습니다.

처리 진입점은 `notes()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_game_controller.py#L117)
