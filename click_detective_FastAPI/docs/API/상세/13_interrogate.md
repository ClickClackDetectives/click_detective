# 13. 캐릭터 심문·진술·쟁점 확정

[API 목차](README.md) · [공통 규칙](../공통규칙.md)

## 역할과 호출 시점

`POST /v1/games/{game_id}/interrogations`

캐릭터 심문·진술·쟁점 확정에 사용하는 실제 구현 경로입니다. 수사 상태를 변경하는 행동입니다. 같은 요청의 재전송은 같은 UUID·본문을 유지합니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다. 수사별 `X-Game-Token: <생성 응답의 game_token>`도 필요합니다.

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

입력 형식 예시입니다. 버전·ID·revision은 자신의 응답 값으로 바꾸고 UUID는 새로 생성하세요. 본문의 ID와 값은 자신의 현재 수사 및 카탈로그와 맞춰 사용하세요.

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
3. GameService.reply가 local 생성·검증을 시도하고 기본 설정에서는 실패를 승인 원문으로 복구합니다. 승인 정보가 없으면 중립 답변이며 fixture는 명시적 고정 모드입니다.
4. 모델 대기 뒤 최신 revision을 재검사합니다.
5. 질문 1회·질문/답변·구조화 진술·새 쟁점을 함께 저장합니다.

## 응답

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

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

- 422: 모르는 인물·주제·미열람 자료·DTO. 생성 내부의 입력 토큰 초과는 기본 복구 정책에서 원문 응답으로 처리할 수 있습니다.
- 429: 질문 한도 25회.
- 409: 생성 중 상태 변경·중복 진행·종결.
- 502/504: fallback_on_error=false인 strict 생성·검증 실패/시간 초과. 기본 true에서는 승인 원문 fallback으로 복구하고 정상 질문 1회로 저장합니다.
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

현재 API 진입점은 [app/investigation/api/routes.py의 `interrogate`](../../../app/investigation/api/routes.py#L55)다.

처리 순서는 [GameService](../../코드참조/app/investigation/service.md), 저장 조건은 [Repository](../../코드참조/app/investigation/persistence/repository.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/views/presentation.md)에서 확인한다.

## 응답 출처와 쟁점

stop은 검증된 모델 대사, fixed는 중립/fixture, fallback은 승인 원문 복구입니다. 세 응답 모두 정상 확정되면 질문을 1회 소비합니다. 쟁점이 없는 질문도 답변은 제공하지만 새 쟁점은 생성하지 않습니다. 복구는 승인된 계획만 확정하며 미승인 비밀을 공개하지 않습니다. [전체 응답 정책](../../에이전트/응답과_복구_정책.md)
