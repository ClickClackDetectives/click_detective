# 14. 획득 출처의 정확한 조합으로 추론 생성

`POST /v1/games/{game_id}/inferences`

수사에서 이미 획득한 출처 조합을 제출해 추론 성립 여부를 판정받는다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 익명 수사는 `X-Game-Token`, 계정 수사는 `X-Access-Token`과 해당 계정 문맥으로 접근한다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

| 필드 | 자료형 | 기본/필수 | 의미 |
| --- | --- | --- | --- |
| request_id | UUID | 필수 | 행동마다 새 UUID, 같은 행동 재전송만 유지 |
| expected_revision | 0 이상 정수 | 필수 | 최신 state.revision |
| sources | 출처 객체 배열 | 필수 | 2~4개, 각 {kind:evidence/testimony/derived,id:문자열} |

예시의 UUID는 새로 생성하고, revision과 ID는 현재 수사 응답에서 가져온다.

```json
{
  "request_id": "0000000e-1111-4111-8111-111111111111",
  "expected_revision": 0,
  "sources": [
    {
      "kind": "evidence",
      "id": "1-02"
    },
    {
      "kind": "testimony",
      "id": "kang-admit-gang_drug"
    }
  ]
}
```

## 서버 처리 순서

1. 출처 종류와 중복·실제 획득을 확인합니다.
2. 직접 선택한 출처 집합이 내부 규칙과 정확히 일치해야 합니다.
3. 규칙의 phase가 현재 단계와 정확히 같은지 검사합니다.
4. 고정 결론과 sourceRefs·leafSources를 저장합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

```json
{
  "request_id": "이번 요청 UUID",
  "result": {
    "id": "derived-reset-glass-entry",
    "kind": "derived",
    "title": "정의된 추론 제목",
    "body": "정의된 결론",
    "sourceRefs": [],
    "leafSources": []
  },
  "state": {
    "id": "수사 UUID",
    "revision": 1
  }
}
```

## 실패·주의점

- 422: 2~4개 위반·중복·미획득·불일치 조합·다른 단계.
- 순서는 달라도 같은 집합입니다. 원본을 다 골랐다고 선행 추론을 대신하지 않습니다.
- 같은 단계에서 같은 결론 재요청은 기존 문서를 반환하며 개수를 늘리지 않습니다.

처리 진입점은 `infer()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_game_controller.py#L87)
