# API 상세 목차

[API 안내](../README.md) · [공통 규칙](../공통규칙.md)

| 메서드·경로 | 상세 설명 |
|---|---|
| `GET /healthz` | [01. 서버 시작 완료 확인](01_health.md) |
| `GET /v1/catalog` | [02. 초기 화면용 공개 데이터](02_catalog.md) |
| `GET /v1/cases` | [03. 실제 시작 가능한 사건 목록](03_cases.md) |
| `GET /v1/cases/{case_id}` | [04. 특정 사건의 공개 카탈로그](04_case_detail.md) |
| `GET /v1/assets/{asset_path:path}` | [05. 소개·인물 이미지·영상](05_public_asset.md) |
| `POST /v1/games` | [06. 새 수사와 게임 토큰 생성](06_create_game.md) |
| `GET /v1/games/{game_id}` | [07. 수사 복원과 화면 상태 집계](07_get_game.md) |
| `GET /v1/games/{game_id}/materials` | [08. 자료 목록·서버 필터·검색](08_materials.md) |
| `GET /v1/games/{game_id}/materials/{material_key}` | [09. 획득한 자료 본문](09_material_detail.md) |
| `GET /v1/games/{game_id}/evidence-assets/{evidence_id}` | [10. 열람한 원본 자료의 이미지](10_evidence_asset.md) |
| `GET /v1/games/{game_id}/findings` | [11. 발견한 쟁점 조회](11_findings.md) |
| `POST /v1/games/{game_id}/examinations` | [12. 자료 열람 확정](12_examine.md) |
| `POST /v1/games/{game_id}/interrogations` | [13. 캐릭터 심문·진술·쟁점 확정](13_interrogate.md) |
| `POST /v1/games/{game_id}/inferences` | [14. 획득 출처의 정확한 조합으로 추론 생성](14_infer.md) |
| `POST /v1/games/{game_id}/phase-transitions` | [15. 조건을 충족한 2차 조사 시작](15_advance.md) |
| `PUT /v1/games/{game_id}/notes` | [16. 메모 전체 저장](16_notes.md) |
| `POST /v1/games/{game_id}/accusations` | [17. 최종 고발 판정과 종결](17_accuse.md) |
| `GET /v1/games/{game_id}/views/{screen}` | [원본 Next.js 화면용 조회 API](18_원본화면_조회.md) |
