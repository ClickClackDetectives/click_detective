# 15. 조건을 충족한 2차 조사 시작

[API 목차](README.md) · [공통 규칙](../06_API_공통규칙과_전체목록.md)

## 역할과 호출 시점

`POST /v1/games/{game_id}/phase-transitions`

조건을 충족한 2차 조사 시작에 사용하는 실제 구현 경로입니다. 수사 상태를 변경하는 행동입니다. 같은 요청의 재전송은 같은 UUID·본문을 유지합니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다. 수사별 `X-Game-Token: <생성 응답의 game_token>`도 필요합니다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

| 필드 | 자료형 | 기본/필수 | 의미 |
| --- | --- | --- | --- |
| request_id | UUID | 필수 | 행동마다 새 UUID, 같은 행동 재전송만 유지 |
| expected_revision | 0 이상 정수 | 필수 | 최신 state.revision |
| target_phase | 정수 | 2 | 2만 허용 |

입력 형식 예시입니다. 버전·ID·revision은 자신의 응답 값으로 바꾸고 UUID는 새로 생성하세요. 본문의 ID와 값은 자신의 현재 수사 및 카탈로그와 맞춰 사용하세요.

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

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

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
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

[app/main.py의 advance()](../../app/main.py#L191)에서 시작합니다. 생성·변경은 [GameService](../파이썬_파일별_상세/app/service.md), 저장은 [Repository](../파이썬_파일별_상세/app/repository.md), 화면 상태는 [Presenter](../파이썬_파일별_상세/app/presentation.md)를 확인하세요.
