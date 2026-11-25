# 12. 자료 열람 확정

[API 목차](README.md) · [공통 규칙](../공통규칙.md)

## 역할과 호출 시점

`POST /v1/games/{game_id}/examinations`

자료 열람 확정에 사용하는 실제 구현 경로입니다. 수사 상태를 변경하는 행동입니다. 같은 요청의 재전송은 같은 UUID·본문을 유지합니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다. 수사별 `X-Game-Token: <생성 응답의 game_token>`도 필요합니다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

| 필드 | 자료형 | 기본/필수 | 의미 |
| --- | --- | --- | --- |
| request_id | UUID | 필수 | 행동마다 새 UUID, 같은 행동 재전송만 유지 |
| expected_revision | 0 이상 정수 | 필수 | 최신 state.revision |
| evidence_id | 문자열 | 필수 | 원본 ID. 예: 1-01 |

입력 형식 예시입니다. 버전·ID·revision은 자신의 응답 값으로 바꾸고 UUID는 새로 생성하세요. 본문의 ID와 값은 자신의 현재 수사 및 카탈로그와 맞춰 사용하세요.

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

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

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
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

현재 API 진입점은 [app/investigation/api/routes.py의 `examine`](../../../app/investigation/api/routes.py#L40)다.

처리 순서는 [GameService](../../코드참조/app/investigation/service.md), 저장 조건은 [수사 저장](../../서버/수사_저장.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/views/presentation.md)에서 확인한다.
