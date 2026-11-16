# 06. 새 수사와 게임 토큰 생성

[API 목차](README.md) · [공통 규칙](../공통규칙.md)

## 역할과 호출 시점

`POST /v1/games`

새 수사와 게임 토큰 생성에 사용하는 실제 구현 경로입니다. 새 수사를 생성하고 이후 호출에 사용할 비밀 토큰을 발급합니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다.

## 입력

| 필드 | 자료형 | 기본/필수 | 의미 |
| --- | --- | --- | --- |
| request_id | UUID | 필수 | 이번 생성 요청 UUID |
| case_id | 문자열 | thirteenth-bell-v1 | 실제 사건 ID |
| scenario_version | 문자열 | 필수 | 카탈로그에서 받은 현재 버전 |

입력 형식 예시입니다. 버전·ID·revision은 자신의 응답 값으로 바꾸고 UUID는 새로 생성하세요. 본문의 ID와 값은 자신의 현재 수사 및 카탈로그와 맞춰 사용하세요.

```json
{
  "request_id": "11111111-1111-4111-8111-111111111111",
  "case_id": "thirteenth-bell-v1",
  "scenario_version": "snapshot-현재카탈로그값"
}
```

## 서버 처리 순서

1. 실제 사건·시나리오 버전을 확인합니다.
2. Repository.create()에서 UUID 중복을 검사합니다.
3. 새 수사 UUID·시각·비밀 게임 토큰·초기 상태를 만듭니다.
4. 같은 생성 요청은 같은 game_id·game_token·state를 반환합니다.

## 응답

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

```json
{
  "game_id": "새 수사 UUID",
  "game_token": "이 수사의 비밀값",
  "state": {
    "id": "새 수사 UUID",
    "revision": 0,
    "phase": 1
  }
}
```

## 실패·주의점

- 409: 오래된 시나리오 버전·같은 UUID의 다른 내용.
- 404: 제공하지 않는 사건.
- 현재 기본 상태 코드는 201이 아니라 200입니다.
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

현재 API 진입점은 [app/investigation/routes.py의 `create_game`](../../../app/investigation/routes.py#L12)다.

처리 순서는 [GameService](../../코드참조/app/investigation/service.md), 저장 조건은 [Repository](../../코드참조/app/investigation/repository.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/presentation.md)에서 확인한다.
