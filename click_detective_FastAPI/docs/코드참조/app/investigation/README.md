# 수사와 저장

[코드 참조 홈](../../README.md)

수사 규칙과 승인 계획을 적용한다. MongoDB에서 요청 예약과 결과 확정을 처리한다.

## 패키지

- [`__init__.py`](__init__.md)

## HTTP 컨트롤러

- [`controllers/investigation_account_controller.py`](controllers/investigation_account_controller.md)
- [`controllers/investigation_game_controller.py`](controllers/investigation_game_controller.md)
- [`controllers/investigation_material_controller.py`](controllers/investigation_material_controller.md)
- [`controllers/investigation_request_context.py`](controllers/investigation_request_context.md)
- [`controllers/investigation_view_controller.py`](controllers/investigation_view_controller.md)

## 서비스와 규칙

- [`services/interrogation/investigation_approval_materials.py`](services/interrogation/investigation_approval_materials.md)
- [`services/interrogation/investigation_free_questions.py`](services/interrogation/investigation_free_questions.md)
- [`services/interrogation/investigation_interrogation_planner.py`](services/interrogation/investigation_interrogation_planner.md)
- [`services/investigation_dialogue_request.py`](services/investigation_dialogue_request.md)
- [`services/investigation_game_service.py`](services/investigation_game_service.md)
- [`services/rules/investigation_accusation_rules.py`](services/rules/investigation_accusation_rules.md)
- [`services/rules/investigation_evidence_rules.py`](services/rules/investigation_evidence_rules.md)
- [`services/rules/investigation_rule_engine.py`](services/rules/investigation_rule_engine.md)
- [`services/rules/investigation_testimony_rules.py`](services/rules/investigation_testimony_rules.md)
- [`services/views/investigation_material_display.py`](services/views/investigation_material_display.md)
- [`services/views/investigation_presenter.py`](services/views/investigation_presenter.md)
- [`services/views/investigation_result_display.py`](services/views/investigation_result_display.md)
- [`services/views/investigation_screen_views.py`](services/views/investigation_screen_views.md)
- [`services/views/investigation_timeline.py`](services/views/investigation_timeline.md)

## 데이터 계약

- [`dto/investigation_command_dto.py`](dto/investigation_command_dto.md)
- [`dto/investigation_interrogation_plan_dto.py`](dto/investigation_interrogation_plan_dto.md)

## 저장소

- [`repositories/investigation_access.py`](repositories/investigation_access.md)
- [`repositories/investigation_evidence_image_repository.py`](repositories/investigation_evidence_image_repository.md)
- [`repositories/investigation_mongo_documents.py`](repositories/investigation_mongo_documents.md)
- [`repositories/investigation_mongo_odm.py`](repositories/investigation_mongo_odm.md)
- [`repositories/investigation_mongo_ownership.py`](repositories/investigation_mongo_ownership.md)
- [`repositories/investigation_mongo_repository.py`](repositories/investigation_mongo_repository.md)
- [`repositories/investigation_mongo_schema.py`](repositories/investigation_mongo_schema.md)
- [`repositories/investigation_mongo_storage.py`](repositories/investigation_mongo_storage.md)
- [`repositories/investigation_mongo_transitions.py`](repositories/investigation_mongo_transitions.md)
- [`repositories/investigation_storage.py`](repositories/investigation_storage.md)

## 의존성 조립

- [`providers/investigation_provider.py`](providers/investigation_provider.md)
