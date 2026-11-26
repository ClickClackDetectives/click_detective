# 12. 자료 열람 확정

`POST /v1/games/{game_id}/examinations`

자료 열람을 수사 상태에 반영한다. 이후 조회부터 확정된 열람 상태가 적용된다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 익명 수사는 `X-Game-Token`, 계정 수사는 `X-Access-Token`과 해당 계정 문맥으로 접근한다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

| 필드 | 자료형 | 기본/필수 | 의미 |
| --- | --- | --- | --- |
| request_id | UUID | 필수 | 행동마다 새 UUID, 같은 행동 재전송만 유지 |
| expected_revision | 0 이상 정수 | 필수 | 최신 state.revision |
| evidence_id | 문자열 | 필수 | 원본 ID. 예: 1-01 |

예시의 UUID는 새로 생성하고, revision과 ID는 현재 수사 응답에서 가져온다.

```json
{
  "request_id": "0000000c-1111-4111-8111-111111111111",
  "expected_revision": 0,
  "evidence_id": "1-01"
}
```

## 서버 처리 순서

1. 공통 예약·revision·종결 상태를 검사합니다.
2. 현재 단계에서 공개된 원본인지 확인합니다.
3. examined에 없을 때만 추가하고 공개 상태를 반환합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

```json
{
  "request_id": "이번 요청 UUID",
  "result": {
    "material_id": "1-01"
  },
  "state": {
    "id": "수사 UUID",
    "revision": 1
  }
}
```

## 실패·주의점

- 404: 없는 원본·미래 단계 원본.
- 같은 자료 반복 열람은 상태가 같아 revision을 늘리지 않습니다.

처리 진입점은 `examine()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_game_controller.py#L57)
