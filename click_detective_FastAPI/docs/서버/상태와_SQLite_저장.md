# 04. 데이터·수사 상태·SQLite

[목차](../README.md) · [저장 코드 설명](../코드참조/app/investigation/persistence/repository.md)

## 1. 데이터 복사와 실제 사용

사건 데이터는 프로젝트의 `data`에서 읽습니다. `data/public`은 이미지·영상, `data/case`는 게임에 사용할 JSON, `data/manifest.json`은 파일 무결성 정보를 담습니다. 모델과 어댑터의 준비·설정은 [설치 안내](../시작하기/02_설치와_실행.md)에서 별도로 확인합니다.

Catalog는 data/manifest.json에 나열된 파일의 해시를 시작 시 검증합니다. manifest 자체의 해시에서 snapshot 버전을 계산합니다. 런타임은 Next.js나 TypeScript 함수를 실행하지 않습니다.

## 2. 사건 JSON

| 파일                                              | 내용                          | 공개 방식                                 |
| ------------------------------------------------- | ----------------------------- | ----------------------------------------- |
| case.json                                         | 사건 소개·선택지·공개 일정    | 카탈로그 DTO                              |
| characters.json                                   | 인물 5명·소개·질문 주제       | 카탈로그 DTO                              |
| evidence.json                                     | 원본 자료 29개·단계·이미지    | 단계별 목록, 열람 후 본문                 |
| testimony-templates.private.json                  | 동선·관계·인정 후보           | 이번 승인 계획의 일부만                   |
| findings.private.json                             | 쟁점 10개·필요 자료           | 발견된 결과만                             |
| inferences.private.json                           | 추론 10개·출처 조합           | 생성한 결과만                             |
| game-rules.json                                   | 질문 한도·단계·고발·진행 규칙 | 판정과 공개 계산값                        |
| initial-state.json                                | 초기 수사 상태                | 새 ID·시각으로 구성                       |
| solution.private.json                             | 정답·해설·채점                | 고발 종결 결과                            |
| character-scripts.private.json                    | 인물별 비공개 대본·출처 쪽수  | 모델 전체 입력 금지, 출처 메타데이터 사용 |
| story-presentation.json                           | 소개 화면 원문                | 일부 공개 블록                            |
| application-data.json                             | 사건 선택용 콘텐츠            | catalog.application                       |
| dialogue-rules.private.json / screen-content.json | TS 분기·문구 기록             | 현재 Python에서 자동 실행하지 않음        |

카탈로그에는 application의 예정 사건도 있을 수 있습니다. 실제 시작 가능한 사건은 /v1/cases에 나온 현재 사건뿐입니다. 화면에서 예정 항목을 실행 가능한 사건으로 가정하지 마세요.

사건 데이터를 수정하려면 manifest의 해당 해시도 갱신해야 합니다. 현재 자동 재수출·마이그레이션 도구는 없습니다. 기존 수사의 scenarioVersion과 달라지면 조회·변경에 충돌이 발생하므로 실행 중인 수사의 버전 정책도 필요합니다.

## 3. 저장 상태의 주요 필드

| 필드                            | 의미                                |
| ------------------------------- | ----------------------------------- |
| id / caseId                     | 수사 ID / 사건 ID                   |
| scenarioVersion / revision      | 정적 데이터 버전 / 변경된 상태 버전 |
| startedAt / phase               | 시작 시각 / 조사 단계 1·2           |
| examined                        | 실제 열람한 원본 ID                 |
| statements                      | 실제 제공한 구조화 진술, ID별 객체  |
| contradictions / findingDetails | 발견한 쟁점 제목 / 상세 출처        |
| revealed                        | 이미 인정한 쟁점 flag               |
| derivedEvidence                 | 생성한 추론 문서                    |
| messages                        | 인물별 질문·대사 기록               |
| notes                           | 메모                                |
| questions                       | 소비한 심문 횟수                    |
| verdict                         | 종결 전 null, 종결 후 판정          |

statements는 최초 확보 ID를 유지합니다. 같은 ID가 있으면 덮어쓰지 않습니다. 다른 주장·인정은 안정된 별도 ID와 supersedes 메타데이터를 사용할 수 있습니다.

## 4. SQLite 테이블

SQLite는 별도 서버 없이 로컬 파일로 사용하는 DB입니다. 기본 파일은 .data/games.sqlite3입니다.

| 테이블     | 열                                                        | 역할                              |
| ---------- | --------------------------------------------------------- | --------------------------------- |
| games      | id, token_hash, revision, state                           | 수사별 권한과 전체 저장 상태 JSON |
| operations | id, game_id, digest, status, nonce, lease_until, response | 행동 중복·진행 예약·완료 재전송   |

질문·대사·메모는 state JSON에 저장됩니다. 원본 모델 프롬프트·검증 출력 전체를 저장하는 테이블은 없습니다. games의 게임 토큰은 해시지만, 생성 재전송을 위해 operations.response에 최초 생성 응답의 game_token이 들어갈 수 있습니다. DB 파일 자체도 서버 전용 비밀 자료로 취급해야 합니다.

## 5. request_id와 revision

같은 수사에서 같은 request_id·행동·내용의 완료 요청은 저장 결과를 반환합니다. 같은 UUID의 내용이 다르면 409입니다. 다른 행동에는 다른 UUID를 사용합니다.

expected_revision은 현재 공개 상태의 revision을 전달합니다. 새 요청의 버전이 오래됐으면 409이고, 이미 완료된 같은 요청의 재전송은 캐시를 먼저 확인합니다. 중복 열람·기존 추론 반환처럼 실제 상태가 같으면 revision을 증가시키지 않습니다.

## 6. pending과 lease

reserve는 짧은 BEGIN IMMEDIATE 트랜잭션에서 요청의 실행권과 nonce를 저장합니다. 같은 요청이 진행 중이면 409 operation_in_progress입니다. lease는 예약 유효 시간이며 현재 전체 시간 제한의 두 배 + 30초입니다.

모델 작업 뒤 commit은 nonce·pending 상태·기준 revision을 다시 검사합니다. 다른 행동이 이미 바꾼 상태 위에 대사를 덮어쓰지 않습니다. 실패 시 abort는 자신의 pending만 failed로 바꾸고 내용이 같은 요청의 재시도를 허용합니다. 만료 후 새 예약의 nonce가 바뀌면 예전 실행은 확정할 수 없습니다.

## 7. SQL 값 전달

사용자 값은 ? 자리표시자에 별도 인자로 바인딩합니다. 질문이나 메모를 SQL 문자열에 직접 붙이지 않습니다. 상태 내용이 SQL 문법처럼 생겨도 데이터로 저장합니다. 다만 이것이 사용자 인증·파일 권한·운영 백업까지 대신하는 것은 아닙니다.

## fallback도 확정된 대화입니다

기본 플레이에서는 모델 오류를 승인 원문으로 복구한 뒤 같은 commit 경로를 사용합니다. 이때 질문 1회와 대화 쌍을 저장하고 승인 계획의 증언·쟁점도 반영합니다. fallback은 failed 예약이 아니라 완료된 응답이므로 같은 UUID 재전송에서 중복 반영하지 않습니다. 실패 무소비는 strict 모드 또는 실제로 확정되지 못한 변경에 대한 설명입니다.

## 현재 구현 위치

- [Catalog](../../app/cases/catalog.py): 사건 파일 읽기와 공개 카탈로그
- [Repository](../../app/investigation/persistence/repository.py): 소유권·예약·버전·확정 저장
- [InvestigationStorage](../../app/investigation/persistence/storage.py): SQLite 연결과 트랜잭션
- [GameService](../../app/investigation/service.py): 예약부터 확정까지 처리 순서
