# 06. API 공통 규칙과 전체 목록

[목차](README.md) · [API별 상세 문서](API_상세/README.md)

## 1. 주소와 메서드

기본 실행 예는 http://127.0.0.1:8000 입니다. GET은 조회, POST는 행동·생성, PUT은 메모 전체 저장에 사용합니다. 경로의 {game_id}는 POST /v1/games의 game_id 값입니다.

## 2. 인증 두 종류

| 헤더                            | 사용 범위                | 의미                                 |
| ------------------------------- | ------------------------ | ------------------------------------ |
| Authorization: Bearer <API_KEY> | 모든 /v1 경로            | .env의 CLICK_API_KEY, Next.js 서버용 |
| X-Game-Token: <GAME_TOKEN>      | /v1/games/{game_id} 아래 | 생성 시 발급된 해당 수사의 비밀 토큰 |

/healthz와 API 문서 경로는 인증 없이 확인할 수 있습니다. 모델/DB가 성공적으로 준비된 뒤 서비스가 요청을 받습니다.

서비스 키가 틀리면 401입니다. 게임 토큰이 없거나 틀리면 해당 수사가 없는 것처럼 404입니다. 수사 ID만 아는 것으로 접근할 수 없습니다. Next.js의 HttpOnly 쿠키 저장·프록시는 권장 연결 방식이며 현재 이 저장 코드가 자동 구현된 것은 아닙니다.

## 3. 입력과 응답의 이름

공통 Key 문자열은 공백 정리 후 1~128자입니다. UUID 필드는 실제 UUID 형식을 검사합니다.

변경 요청은 snake_case인 expected_revision, suspect_id 등을 사용합니다. 공개 state는 기존 화면과 맞춘 camelCase인 caseId, scenarioVersion, derivedEvidence 등을 사용합니다. 이름을 임의로 바꾸면 extra=forbid 규칙으로 422가 날 수 있습니다.

## 4. 공통 변경 요청

```json
{
  "request_id": "f3a53f41-679c-488c-9315-b28b0f6efc00",
  "expected_revision": 0
}
```

각 행동의 고유 필드를 추가합니다. UUID는 행동마다 새로 만들고 네트워크 재전송에서만 유지합니다. expected_revision은 최신 state.revision입니다. 같은 UUID로 질문이나 행동 종류를 바꾸면 409입니다.

응답 형태:

```json
{
  "request_id": "f3a53f41-679c-488c-9315-b28b0f6efc00",
  "result": { "saved": true },
  "state": { "id": "수사-ID", "revision": 1 }
}
```

위 state는 설명을 위해 줄였습니다. 실제 응답에는 전체 공개 상태가 있습니다. 생성 API는 game_id·game_token·state를 반환하므로 별도 형식입니다. 같은 완료 요청 재전송은 당시 저장된 결과를 반환하므로 현재 화면보다 낮은 revision 응답을 늦게 적용하지 않도록 화면에서도 구분해야 합니다.

## 5. 공개 state의 계산 필드

materials는 현재 공개 가능한 자료 요약, inferenceSources는 실제 획득한 연결 후보, progress는 counts/goals/completed/total/percent, availableActions는 interrogate/advance/accuse/notes 여부입니다. 버튼 활성화에는 사용할 수 있지만 실제 POST에서 서버가 조건을 다시 검사합니다.

## 6. 자료 ID 세 가지

- evidence:1-01: 원본 자료
- testimony:kang-admit-gang_drug: 기록된 진술
- derived:derived-reset-glass-entry: 생성한 추론

상세 GET에는 kind:ID 형식인 material_key를 사용합니다. 반면 심문의 material_id는 원본 ID 또는 derived-... ID만 사용합니다. 심문에서 구조화 진술 ID를 자료로 제시하는 것은 현재 지원하지 않습니다. 추론 sources는 kind/id 객체 목록이며 kind는 evidence/testimony/derived입니다. 외부 API 값으로 inference를 보내면 현재 DTO가 받지 않습니다.

## 7. 실제 API 18개

| 번호 | API                                                   | 역할                      |
| ---- | ----------------------------------------------------- | ------------------------- |
| 1    | GET /healthz                                          | 시작 완료 확인            |
| 2    | GET /v1/catalog                                       | 화면 초기 카탈로그        |
| 3    | GET /v1/cases                                         | 실제 시작 가능 사건       |
| 4    | GET /v1/cases/{case_id}                               | 특정 사건의 공개 카탈로그 |
| 5    | GET /v1/assets/{asset_path}                           | 소개·인물·영상 자산       |
| 6    | POST /v1/games                                        | 수사 생성·게임 토큰 발급  |
| 7    | GET /v1/games/{game_id}                               | 전체 공개 수사 상태       |
| 8    | GET /v1/games/{game_id}/materials                     | 자료 목록·필터·검색       |
| 9    | GET /v1/games/{game_id}/materials/{material_key}      | 획득 자료 본문            |
| 10   | GET /v1/games/{game_id}/evidence-assets/{evidence_id} | 열람 증거 이미지          |
| 11   | GET /v1/games/{game_id}/findings                      | 발견 쟁점만 조회          |
| 12   | POST /v1/games/{game_id}/examinations                 | 열람 확정                 |
| 13   | POST /v1/games/{game_id}/interrogations               | 심문·진술·쟁점 확정       |
| 14   | POST /v1/games/{game_id}/inferences                   | 정확한 자료 연결          |
| 15   | POST /v1/games/{game_id}/phase-transitions            | 2차 조사 전환             |
| 16   | PUT /v1/games/{game_id}/notes                         | 메모 전체 저장            |
| 17   | POST /v1/games/{game_id}/accusations                  | 최종 고발·종결            |

각 API의 요청 예·출력·호출 코드·실패 조건은 [API 상세 폴더](API_상세/README.md)에 있습니다.

## 8. 오류 읽기

| 상태      | 뜻                                                                                      |
| --------- | --------------------------------------------------------------------------------------- |
| 200       | 정상 처리. 새 생성도 현재 기본 상태는 200                                               |
| 206       | 영상 등 파일의 Range 부분 응답                                                          |
| 401       | 서비스 인증 실패                                                                        |
| 404       | 사건·수사·자산 없음 또는 접근 불가                                                      |
| 409       | UUID 내용 충돌·진행 중·revision/시나리오 충돌·종결 후 변경                              |
| 422       | 입력 검증·미획득 자료·잘못된 출처 조합·단계 조건·로컬 생성 입력 초과                    |
| 429       | 질문 한도 초과                                                                          |
| 502 / 504 | strict 모드의 생성·검증 실패 / 시간 초과. 기본 플레이에서는 승인 원문 fallback으로 복구 |

Pydantic 오류는 입력 원문 대신 loc·type을 반환합니다. 생성 오류에는 가능한 경우 X-Generation-Error 헤더에 고정 원인 코드가 있습니다. 전체 private JSON을 읽는 HTTP API는 없습니다.

## 원본 UI 연결용 추가 조회

[GET /v1/games/{game_id}/views/{screen}](API_상세/18_원본화면_조회.md)는 자료실·증언·추론 검색과 분류를 서버에서 처리합니다.

## 심문 성공 응답의 세 가지 출처

기본 플레이 심문은 stop(검증된 생성), fixed(중립/fixture), fallback(승인 원문 복구)을 구분합니다. 세 응답 모두 정상 확정되면 질문 1회·대화가 저장됩니다. 인증·입력·상태 충돌·네트워크 오류는 별도입니다. [상세 정책](12_질문_응답과_복구_정책.md)

화면 전용 조회까지 포함하면 업무 경로는 18개입니다. [원본 화면 조회](API_상세/18_원본화면_조회.md)도 서비스 인증과 수사 토큰을 검사합니다. 최종 고발은 현재 미종결 수사에서 준비도와 관계없이 가능하며 근거 부족은 채점으로 처리합니다.
