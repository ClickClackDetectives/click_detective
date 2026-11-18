# API 연결표와 요청 예제

브라우저의 호출·Next.js 중계·FastAPI 경로를 현재 `commands.ts`와 `policy.ts` 기준으로 연결합니다. 인증·재시도는 [상태 관리](인증과_상태관리.md), 함수 선언은 [서버 중계 코드](../코드참조/서버/API중계.md)에서 확인합니다.

## 1. 세 단계의 이름을 구분하기

같은 행동이라도 원본 컨트롤러 이름, 브라우저 BFF 경로, FastAPI 경로가 다릅니다.

```text
updateGame('examine', { evidenceId: '1-01' })
  → requestGame이 필드 변환 및 UUID·revision 추가
  → POST /api/detective/examinations
  → POST /v1/games/{game_id}/examinations
```

브라우저 호출의 기본 접두사는 `/api/detective/`입니다. 아래 표의 짧은 경로 앞에 이 접두사를 붙여 읽으세요. `{game_id}`는 Next.js가 쿠키에서 읽으므로 화면이 임의의 게임 ID를 본문으로 지정하지 않습니다.

## 2. 전체 경로 대응

| 메서드 | BFF 경로               | FastAPI 경로                               | 역할                                       |
| ------ | ---------------------- | ------------------------------------------ | ------------------------------------------ |
| GET    | `health`               | `/healthz`                                 | 서버 준비 확인                             |
| GET    | `catalog`              | `/v1/catalog`                              | 사건·인물·선택지·사건 카드·표시 메타데이터 |
| GET    | `cases`                | `/v1/cases`                                | 실제 시작 가능한 사건 목록                 |
| GET    | `cases/{case_id}`      | `/v1/cases/{case_id}`                      | 사건별 공개 카탈로그                       |
| GET    | `assets/{path}`        | `/v1/assets/{path}`                        | 공개 이미지·영상                           |
| POST   | `start`                | `/v1/games`                                | 수사 생성 및 쿠키 발급                     |
| GET    | `state`                | `/v1/games/{game_id}`                      | 현재 수사 복원                             |
| GET    | `materials`            | `/v1/games/{game_id}/materials`            | 자료 목록·기본 필터                        |
| GET    | `materials/{kind:id}`  | `/v1/games/{game_id}/materials/{kind:id}`  | 획득한 자료 본문                           |
| GET    | `evidence-assets/{id}` | `/v1/games/{game_id}/evidence-assets/{id}` | 획득한 원본 이미지                         |
| GET    | `findings`             | `/v1/games/{game_id}/findings`             | 발견한 쟁점 목록                           |
| GET    | `views/{screen}`       | `/v1/games/{game_id}/views/{screen}`       | 원본 자료실·증언·추론 화면 검색            |
| POST   | `examinations`         | `/v1/games/{game_id}/examinations`         | 자료 열람 확정                             |
| POST   | `interrogations`       | `/v1/games/{game_id}/interrogations`       | 대사 생성·검증·대화 기록                   |
| POST   | `inferences`           | `/v1/games/{game_id}/inferences`           | 출처 조합에 따른 추론                      |
| POST   | `phase-transitions`    | `/v1/games/{game_id}/phase-transitions`    | 2차 조사 전환                              |
| PUT    | `notes`                | `/v1/games/{game_id}/notes`                | 메모 전체 저장                             |
| POST   | `accusations`          | `/v1/games/{game_id}/accusations`          | 고발 검증·판정·종결                        |

현재 FastAPI의 업무 경로는 패턴 기준 18개입니다. `views/evidence`, `views/testimonies`, `views/inference`는 하나의 `/views/{screen}` 패턴을 사용합니다.

화면은 모든 조회 API를 매번 호출하지 않습니다. 예를 들어 쟁점 화면은 전체 state의 `findingDetails`도 사용하고, 홈 사건 카드에는 `catalog.application.cases`를 사용합니다. 카탈로그의 준비 중 카드와 `/cases`의 실제 시작 가능 사건 목록은 목적이 다릅니다.

## 3. 원본 행동 이름 변환

| 원본 행동          | 원본 입력                                             | FastAPI 추가 입력                                        |
| ------------------ | ----------------------------------------------------- | -------------------------------------------------------- |
| `examine`          | `evidenceId`                                          | `evidence_id`                                            |
| `interrogate`      | `suspectId`, `question`, 선택 `topicId`, `evidenceId` | `suspect_id`, `question`, 선택 `topic_id`, `material_id` |
| `connect-evidence` | `sources`                                             | `sources`                                                |
| `advance`          | 빈 객체                                               | `target_phase: 2`                                        |
| `notes`            | `text`                                                | `text`                                                   |
| `accuse`           | `suspectId`, `motive`, `method`, `evidenceIds`        | `suspect_id`, `motive`, `method`, `evidence_ids`         |

변환 코드는 `app/game/investigation/commands.ts`의 `mapGameCommand`에 있습니다. 화면이 사용하는 기존 이름을 유지하기 위한 어댑터이며 정답을 판정하는 엔진은 아닙니다.

## 4. 공통 변경 계약

생성을 제외한 변경 요청에는 다음 두 필드가 붙습니다.

```json
{
  "request_id": "d82c1b87-7b47-483c-a6d9-27eb22ddbfcb",
  "expected_revision": 3
}
```

`request_id`는 행동 고유 번호이고 `expected_revision`은 현재 확인한 저장 버전입니다. 다음 예시의 UUID와 revision은 설명용입니다. 그대로 재사용하지 말고 실제 최신 상태로 구성해야 합니다.

열람 요청 예시:

```json
{
  "request_id": "d82c1b87-7b47-483c-a6d9-27eb22ddbfcb",
  "expected_revision": 3,
  "evidence_id": "1-02"
}
```

심문 요청 예시:

```json
{
  "request_id": "3cc02be0-f43e-4817-9903-e56cad245292",
  "expected_revision": 4,
  "suspect_id": "kang",
  "question": "와인잔과 약의 경위를 설명하세요.",
  "material_id": "1-02"
}
```

승인 사실·정답·최종 reply를 화면이 함께 지정하지 않습니다. 실제 계획과 사실 선택은 FastAPI가 수행합니다.

변경 성공 응답은 `{request_id, result, state}`입니다. 컨트롤러가 사용하는 `requestGame`은 이 중 `state`를 반환하므로, 화면은 `result`를 바탕으로 진행률을 다시 계산할 필요가 없습니다.

## 5. 생성과 이어하기

새 생성 본문은 `{request_id, case_id, scenario_version}`입니다. FastAPI는 `{game_id, game_token, state}`를 반환하지만 BFF는 토큰을 쿠키로 옮기고 브라우저 JSON에는 `{state}`만 보냅니다.

원본 ‘수사 이어하기’는 최신 기록이 메모리에 있으면 이를 반환해 화면을 이동합니다. 이어하기 클릭마다 무조건 새로운 `/games`를 만드는 것은 아닙니다. ‘다시 수사하기’에서 `restart: true`를 사용하면 새 생성 요청을 보냅니다. `restart`는 프런트엔드 어댑터의 옵션이고 FastAPI 생성 DTO에 그대로 전달하지 않습니다.

## 6. 목록과 본문 구분

자료 키는 종류와 ID를 합칩니다.

| 키 예시                | 의미                 |
| ---------------------- | -------------------- |
| `evidence:1-01`        | 원본 자료            |
| `testimony:실제증언ID` | 수사 중 기록된 증언  |
| `derived:실제추론ID`   | 서버에서 생성한 추론 |

주소에 넣을 때 `encodeURIComponent`를 사용합니다. 심문 첨부의 `material_id`에는 이 접두사 전체가 아니라 서버가 요구하는 원본 또는 추론의 ID를 보냅니다. 추론 출처 `sources`에는 `{kind, id}`를 따로 넣습니다.

카탈로그의 `display.evidence`는 제목·요약 등 메타데이터를 제공하며 본문은 빈 문자열입니다. 실제 본문은 획득 권한을 확인한 상세 API로 읽습니다.

## 7. 화면별 조회 API

| screen        | 조건                 | 응답 필드                                    |
| ------------- | -------------------- | -------------------------------------------- |
| `evidence`    | `search`, `place`    | `available`, `places`, `groups`, `readCount` |
| `testimonies` | `search`, `person`   | 증언자별 `visible`                           |
| `inference`   | `search`, `category` | 출처 목록 `visible`                          |

`testimonies.visible`의 각 항목에는 `initial`, `records`, `acquired`, `pairs`가 있습니다. 화면의 진술 분류 버튼 등 표시용 선택은 UI에서 이어서 적용할 수 있습니다. `inference`의 category는 `evidence`, `testimony`, `derived`입니다.

`materials`의 기본 목록 필터는 `kind`, `archive_kind`, `search`, `place`입니다. `archive_kind=inference`와 출처 category의 `derived`를 혼동하지 마세요.

이미지 없는 자료는 상세 응답의 `illustration`이 `null`입니다. Next.js는 이 경우 이전 이미지 주소를 지우고 그림을 표시하지 않습니다. 2차 증거의 추가 파일 경로는 [FastAPI 이미지 안내](../../../click_detective_FastAPI/docs/게임진행/2차_증거_이미지.md)를 참고하세요.

## 8. 자산과 오류 응답

원본 `/assets/...`와 `/manor.jpg`도 같은 중계 로직으로 처리합니다. 영상은 `Range` 요청을 전달하고 `206`, `Content-Range`, `Accept-Ranges` 등의 응답 정보를 유지합니다.

BFF 오류 형식은 `{error, code}`입니다. 서버 생성 오류의 `X-Generation-Error`가 있으면 코드로 사용하고, 그 외에는 `BACKEND_401`처럼 HTTP 상태 기반 코드를 사용합니다. `operation_in_progress`는 별도로 유지합니다. 자세한 상태별 대응은 [오류 해결](../테스트/검사와_오류해결.md)에 있습니다.

다음 문서: [인증과 상태 관리](인증과_상태관리.md)

## 기본 플레이에서의 심문 복구 응답

백엔드의 `CLICK_FALLBACK_ON_ERROR=true`가 기본값입니다. 생성·검증이 실패하면 승인 원문 대사로 복구하며, 성공 응답에 `finish_reason=fallback`이 표시됩니다. 이 답변은 정상 저장된 질문 1회로 기록합니다. `fixed`는 중립 또는 fixture 응답을 나타냅니다. 복구를 끈 `CLICK_FALLBACK_ON_ERROR=false` 환경에서 생성 오류가 반환되면 BFF는 `X-Generation-Error` 코드를 전달합니다. 자세한 정책은 [FastAPI 응답과 복구 정책](../../../click_detective_FastAPI/docs/에이전트/응답과_복구_정책.md)에 있습니다.

[전체 문서](../README.md)
