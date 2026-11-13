# API별 상세 설명

[전체 목차](../README.md) · [공통 인증·revision·응답](../06_API_공통규칙과_전체목록.md)

| 번호 | 메서드·경로 | 설명 |
| --- | --- | --- |
| 1 | `GET /healthz` | [서버 시작 완료 확인](01_health.md) |
| 2 | `GET /v1/catalog` | [초기 화면용 공개 데이터](02_catalog.md) |
| 3 | `GET /v1/cases` | [실제 시작 가능한 사건 목록](03_cases.md) |
| 4 | `GET /v1/cases/{case_id}` | [특정 사건의 공개 카탈로그](04_case_detail.md) |
| 5 | `GET /v1/assets/{asset_path:path}` | [소개·인물 이미지·영상](05_public_asset.md) |
| 6 | `POST /v1/games` | [새 수사와 게임 토큰 생성](06_create_game.md) |
| 7 | `GET /v1/games/{game_id}` | [수사 복원과 화면 상태 집계](07_get_game.md) |
| 8 | `GET /v1/games/{game_id}/materials` | [자료 목록·서버 필터·검색](08_materials.md) |
| 9 | `GET /v1/games/{game_id}/materials/{material_key}` | [획득한 자료 본문](09_material_detail.md) |
| 10 | `GET /v1/games/{game_id}/evidence-assets/{evidence_id}` | [열람한 원본 자료의 이미지](10_evidence_asset.md) |
| 11 | `GET /v1/games/{game_id}/findings` | [발견한 쟁점 조회](11_findings.md) |
| 12 | `POST /v1/games/{game_id}/examinations` | [자료 열람 확정](12_examine.md) |
| 13 | `POST /v1/games/{game_id}/interrogations` | [캐릭터 심문·진술·쟁점 확정](13_interrogate.md) |
| 14 | `POST /v1/games/{game_id}/inferences` | [획득 출처의 정확한 조합으로 추론 생성](14_infer.md) |
| 15 | `POST /v1/games/{game_id}/phase-transitions` | [조건을 충족한 2차 조사 시작](15_advance.md) |
| 16 | `PUT /v1/games/{game_id}/notes` | [메모 전체 저장](16_notes.md) |
| 17 | `POST /v1/games/{game_id}/accusations` | [최종 고발 판정과 종결](17_accuse.md) |

| 18 | `GET /v1/games/{game_id}/views/{screen}` | [원본 화면 분류·검색](18_원본화면_조회.md) |
