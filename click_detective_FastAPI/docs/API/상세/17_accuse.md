# 17. 최종 고발 판정과 종결

`POST /v1/games/{game_id}/accusations`

고발 내용을 평가하고 수사를 종결한다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 익명 수사는 `X-Game-Token`, 계정 수사는 `X-Access-Token`과 해당 계정 문맥으로 접근한다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

| 필드 | 자료형 | 기본/필수 | 의미 |
| --- | --- | --- | --- |
| request_id | UUID | 필수 | 행동마다 새 UUID, 같은 행동 재전송만 유지 |
| expected_revision | 0 이상 정수 | 필수 | 최신 state.revision |
| suspect_id | 문자열 | 필수 | 인물 ID |
| motive | 문자열 | 필수 | 카탈로그 동기 ID |
| method | 문자열 | 필수 | 카탈로그 수단 ID |
| evidence_ids | 문자열 배열 | 선택, 기본 [] | 실제 추론 ID 0~50개. 생략 시 빈 배열. 중복·획득을 재검사 |

예시의 UUID는 새로 생성하고, revision과 ID는 현재 수사 응답에서 가져온다.

```json
{
  "request_id": "00000011-1111-4111-8111-111111111111",
  "expected_revision": 0,
  "suspect_id": "카탈로그의 인물 ID",
  "motive": "카탈로그의 동기 ID",
  "method": "카탈로그의 수단 ID",
  "evidence_ids": [
    "실제 추론 ID 1",
    "실제 추론 ID 2",
    "실제 추론 ID 3",
    "실제 추론 ID 4",
    "실제 추론 ID 5"
  ]
}
```

## 서버 처리 순서

1. 인물·동기·수단 선택을 검사합니다. 1차 조사부터 제출할 수 있습니다.
2. 제출한 추론 ID가 있으면 실제 생성한 서로 다른 항목인지 확인합니다. 0개도 허용합니다.
3. 조사 단계·진행률·추론 수·쟁점 수는 제출을 차단하지 않습니다.
4. 제출 추론의 원본 근거와 필수 제출 연결을 채점합니다.
5. 4항목 각 25점·해설·근거 평가·검토 목록을 verdict에 저장합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

```json
{
  "request_id": "이번 요청 UUID",
  "result": {
    "correct": true,
    "score": 100,
    "checks": [],
    "submittedEvidenceIds": [],
    "evidenceAssessment": {},
    "review": {},
    "explanation": "종결 후 공개하는 해설"
  },
  "state": {
    "id": "수사 UUID",
    "revision": 1
  }
}
```

## 실패·주의점

- 422: 잘못된 선택값·미확보/중복 추론 제출 등.
- 409: 이미 종결된 수사.
- 근거가 없거나 오답인 고발도 제출되면 종결됩니다. 진행률 100%와는 별도 조건입니다.

## 항상 열려 있는 제출

미종결 수사는 1차 조사부터 고발할 수 있습니다. 추론 증거 선택은 선택 사항이며 목록에 ‘필수’ 표시를 붙이지 않습니다. 핵심 추론·원본 근거 연결은 입증 점수 기준으로 유지하므로 증거 없는 고발은 입증 항목에서 점수를 받지 못합니다. 범인·동기·수단 선택은 필요하며 제출 확정 후에는 기존 종결 정책을 따릅니다.

처리 순서는 [GameService](../../코드참조/app/investigation/services/investigation_game_service.md), 저장 조건은 [수사 저장](../../서버/수사_저장.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/services/views/investigation_presenter.md)에서 확인한다.

처리 진입점은 `accuse()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_game_controller.py#L132)
