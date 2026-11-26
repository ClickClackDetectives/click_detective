# 엔드포인트별 요청과 응답

메서드와 경로를 골라 인증, 요청 예제, 응답 필드와 오류 조건을 확인합니다. [공통 규칙](../공통규칙.md) · [호출 실습](../처음_호출하기.md)

## 서버 상태와 공개 사건

| 경로 | 상세 문서 |
| --- | --- |
| `GET /healthz` | [서버 기동 확인](01_health.md) |
| `GET /v1/catalog` | [웹 첫 화면 카탈로그](02_catalog.md) |
| `GET /v1/cases` | [시작할 수 있는 사건 목록](03_cases.md) |
| `GET /v1/cases/{case_id}` | [선택한 사건의 공개 정보](04_case_detail.md) |
| `GET /v1/assets/{asset_path:path}` | [공개 이미지와 영상](05_public_asset.md) |

## 수사 조회와 상태 변경

| 경로 | 상세 문서 |
| --- | --- |
| `POST /v1/games` | [수사 ID와 게임 토큰 발급](06_create_game.md) |
| `GET /v1/games/{game_id}` | [저장된 수사 상태 불러오기](07_get_game.md) |
| `GET /v1/games/{game_id}/materials` | [획득 자료 검색 및 분류](08_materials.md) |
| `GET /v1/games/{game_id}/materials/{material_key}` | [개별 자료의 본문 불러오기](09_material_detail.md) |
| `GET /v1/games/{game_id}/evidence-assets/{evidence_id}` | [열람 권한이 있는 증거 이미지](10_evidence_asset.md) |
| `GET /v1/games/{game_id}/findings` | [발견한 쟁점 목록](11_findings.md) |
| `POST /v1/games/{game_id}/examinations` | [증거 열람 기록](12_examine.md) |
| `POST /v1/games/{game_id}/interrogations` | [질문과 증거를 제출해 대사 수신](13_interrogate.md) |
| `POST /v1/games/{game_id}/inferences` | [자료 조합을 제출해 추론 확정](14_infer.md) |
| `POST /v1/games/{game_id}/phase-transitions` | [다음 조사 단계로 이동](15_advance.md) |
| `PUT /v1/games/{game_id}/notes` | [수사 메모 교체](16_notes.md) |
| `POST /v1/games/{game_id}/accusations` | [범인과 근거를 제출해 최종 판정](17_accuse.md) |
| `GET /v1/games/{game_id}/views/{screen}` | [화면에 필요한 수사 데이터 조회](18_원본화면_조회.md) |

계정과 내부 모델 검사 경로는 [API 안내](../README.md)에서 찾을 수 있습니다.
