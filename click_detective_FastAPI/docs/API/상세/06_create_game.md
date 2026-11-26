# 06. 새 수사와 게임 토큰 생성

`POST /v1/games`

지정한 사건 버전으로 수사를 생성하고 첫 공개 상태를 받는다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 계정 소유 수사를 만들 때는 `X-Access-Token`을 함께 보낸다. 익명 수사에는 새 게임 토큰이 발급되고 계정 수사의 `game_token`은 null이다.

## 입력

| 필드 | 자료형 | 기본/필수 | 의미 |
| --- | --- | --- | --- |
| request_id | UUID | 필수 | 이번 생성 요청 UUID |
| case_id | 문자열 | thirteenth-bell-v1 | 실제 사건 ID |
| scenario_version | 문자열 | 필수 | 카탈로그에서 받은 현재 버전 |

예시의 UUID는 새로 생성하고, 사건 ID와 버전은 카탈로그에서 가져온다.

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

응답에서 주로 쓰는 필드를 발췌한 예시다.

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

처리 진입점은 `create_game()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_game_controller.py#L26)
