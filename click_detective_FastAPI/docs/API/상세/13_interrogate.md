# 13. 캐릭터 심문·진술·쟁점 확정

`POST /v1/games/{game_id}/interrogations`

서버가 승인한 문맥으로 심문 대사를 생성하고 결과를 수사 기록에 반영한다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 익명 수사는 `X-Game-Token`, 계정 수사는 `X-Access-Token`과 해당 계정 문맥으로 접근한다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

| 필드              | 자료형      | 기본/필수 | 의미                                        |
| ----------------- | ----------- | --------- | ------------------------------------------- |
| request_id        | UUID        | 필수      | 행동마다 새 UUID, 같은 행동 재전송만 유지   |
| expected_revision | 0 이상 정수 | 필수      | 최신 state.revision                         |
| suspect_id        | 문자열      | 필수      | 인물 ID                                     |
| question          | 문자열      | 필수      | 공백 정리 후 1~1000자                       |
| material_id       | 문자열/null | null      | 열람 원본 ID 또는 실제 추론 ID              |
| topic_id          | 문자열/null | null      | movement 또는 about-다른인물ID 등 허용 주제 |

예시의 UUID는 새로 생성하고, revision과 ID는 현재 수사 응답에서 가져온다.

```json
{
  "request_id": "0000000d-1111-4111-8111-111111111111",
  "expected_revision": 0,
  "suspect_id": "kang",
  "question": "그날 밤의 동선을 말씀해 주세요.",
  "topic_id": "movement",
  "material_id": null
}
```

## 서버 처리 순서

1. 인물·질문 한도·주제·실제 획득한 자료를 검사합니다.
2. 인물별 누적 제시 근거와 인정 상태로 승인 계획을 만듭니다.
3. 승인 계획을 준비한 유효한 심문은 접수를 확정하고 질문 1회를 차감합니다.
4. `ReplyService.reply`가 대사를 생성·검증하거나 설정에 맞는 복구 응답을 준비합니다.
5. 최신 revision을 검사한 후 질문·답변과 검증된 진술·쟁점을 저장합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

```json
{
  "request_id": "이번 요청 UUID",
  "result": {
    "reply": "캐릭터 대사",
    "finish_reason": "stop",
    "model_version": "Qwen2.5-7B-Instruct-nf4+provided-adapter",
    "used_fact_ids": ["승인 사실 ID"]
  },
  "state": {
    "id": "수사 UUID",
    "revision": 1
  }
}
```

## 실패·주의점

- 422: 모르는 인물·주제·미열람 자료·DTO. 내부 토큰 한도 초과는 복구를 허용한 경우 중립 응답을 반환할 수 있다.
- 429: 질문 한도 25회.
- 409: 생성 중 상태 변경·중복 진행·종결.
- 502/504: fallback_on_error=false인 strict 생성·검증 실패/시간 초과. 서비스로 전파된 오류는 복구 설정을 따른다. 그래프에서 처리한 생성·검증 실패는 중립 응답이 될 수 있다. 이미 접수한 심문은 응답이 오류여도 1회를 소비합니다.

## 응답 출처와 쟁점

`stop`은 검증된 모델 대사, `fixed`는 고정 대사, `fallback`은 승인 원문 복구다. 검증에서는 `partial`과 `neutral`도 나올 수 있다. 유효한 질문은 접수할 때 1회를 소비하며, 답변이 정상 확정되면 대화가 추가됩니다. 쟁점이 없는 질문도 답변은 제공하지만 새 쟁점은 생성하지 않습니다. 복구는 승인된 계획만 확정하며 미승인 비밀을 공개하지 않습니다. [전체 응답 정책](../../에이전트/응답과_복구_정책.md)

처리 순서는 [GameService](../../코드참조/app/investigation/services/investigation_game_service.md), 저장 조건은 [수사 저장](../../서버/수사_저장.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/services/views/investigation_presenter.md)에서 확인한다.

[심문 응답과 복구 정책](../../에이전트/응답과_복구_정책.md)

처리 진입점은 `interrogate()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_game_controller.py#L72)
