# 11. 발견한 쟁점 조회

`GET /v1/games/{game_id}/findings`

현재 수사에 기록된 쟁점을 확인한다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 익명 수사는 `X-Game-Token`, 계정 수사는 `X-Access-Token`과 해당 계정 문맥으로 접근한다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

## 서버 처리 순서

1. 게임 토큰·버전을 확인합니다.
2. state.findingDetails만 반환합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

```json
{
  "findings": [
    {
      "title": "발견한 쟁점 제목",
      "suspectId": "kang",
      "sourceRefs": [
        {
          "kind": "evidence",
          "id": "1-02"
        }
      ],
      "messageIndex": 1
    }
  ]
}
```

## 실패·주의점

- 아직 발견하지 않은 쟁점의 label·need·reply를 공개하지 않습니다.
- 직접 쟁점을 추가하는 POST는 없습니다. 심문 결과로만 확정합니다.

처리 진입점은 `findings()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_material_controller.py#L116)
