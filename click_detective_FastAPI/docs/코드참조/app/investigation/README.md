# 수사 요청·판정·저장 코드

수사 컨트롤러에서 게임 서비스를 호출합니다. 서비스는 승인 계획과 진행 규칙을 적용하고, MongoDB 저장소에서 상태 변경 요청의 예약과 확정을 처리합니다.

[수사 HTTP 요청](controllers/investigation_game_controller.md) · [게임 서비스](services/investigation_game_service.md) · [MongoDB 상태 전이](repositories/investigation_mongo_transitions.md)

| 소스 폴더 | 파일별 참조 |
| --- | --- |
| `app/investigation/` | [`__init__.py`](__init__.md) |
| `app/investigation/controllers/` | [`investigation_account_controller.py`](controllers/investigation_account_controller.md) · [`investigation_game_controller.py`](controllers/investigation_game_controller.md) · [`investigation_material_controller.py`](controllers/investigation_material_controller.md) · [`investigation_request_context.py`](controllers/investigation_request_context.md) · [`investigation_view_controller.py`](controllers/investigation_view_controller.md) |
| `app/investigation/dto/` | [`investigation_command_dto.py`](dto/investigation_command_dto.md) · [`investigation_interrogation_plan_dto.py`](dto/investigation_interrogation_plan_dto.md) |
| `app/investigation/providers/` | [`investigation_provider.py`](providers/investigation_provider.md) |
| `app/investigation/repositories/` | [`investigation_access.py`](repositories/investigation_access.md) · [`investigation_evidence_image_repository.py`](repositories/investigation_evidence_image_repository.md) · [`investigation_mongo_documents.py`](repositories/investigation_mongo_documents.md) · [`investigation_mongo_odm.py`](repositories/investigation_mongo_odm.md) · [`investigation_mongo_ownership.py`](repositories/investigation_mongo_ownership.md) · [`investigation_mongo_repository.py`](repositories/investigation_mongo_repository.md) · [`investigation_mongo_schema.py`](repositories/investigation_mongo_schema.md) · [`investigation_mongo_storage.py`](repositories/investigation_mongo_storage.md) · [`investigation_mongo_transitions.py`](repositories/investigation_mongo_transitions.md) · [`investigation_storage.py`](repositories/investigation_storage.md) |
| `app/investigation/services/interrogation/` | [`investigation_approval_materials.py`](services/interrogation/investigation_approval_materials.md) · [`investigation_free_questions.py`](services/interrogation/investigation_free_questions.md) · [`investigation_interrogation_planner.py`](services/interrogation/investigation_interrogation_planner.md) |
| `app/investigation/services/` | [`investigation_dialogue_request.py`](services/investigation_dialogue_request.md) · [`investigation_game_service.py`](services/investigation_game_service.md) |
| `app/investigation/services/rules/` | [`investigation_accusation_rules.py`](services/rules/investigation_accusation_rules.md) · [`investigation_evidence_rules.py`](services/rules/investigation_evidence_rules.md) · [`investigation_rule_engine.py`](services/rules/investigation_rule_engine.md) · [`investigation_testimony_rules.py`](services/rules/investigation_testimony_rules.md) |
| `app/investigation/services/views/` | [`investigation_material_display.py`](services/views/investigation_material_display.md) · [`investigation_presenter.py`](services/views/investigation_presenter.md) · [`investigation_result_display.py`](services/views/investigation_result_display.md) · [`investigation_screen_views.py`](services/views/investigation_screen_views.md) · [`investigation_timeline.py`](services/views/investigation_timeline.md) |

[FastAPI 코드 참조](../../README.md)
