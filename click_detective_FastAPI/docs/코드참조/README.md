# 현재 Python 코드 참조

[전체 문서 목차](../README.md)

`app`, `scripts`, `tests`에서 코드 참조가 있는 Python 파일 100개를 다룬다. 함수 본문을 복제하는 대신 실제 선언문, 역할, 파라미터와 반환값을 보여준다. 본문은 각 문서의 소스 링크에서 확인한다.

에이전트를 처음 읽는다면 [전처리](../에이전트/전처리/README.md) → [생성](../에이전트/생성/README.md) → [검증](../에이전트/검증/README.md) 설명부터 읽는다.

## 전처리 에이전트

| 소스 파일 | 설명 |
|---|---|
| `app/dialogue/preprocess_agent/__init__.py` | [문서](app/dialogue/preprocess_agent/__init__.md) |
| `app/dialogue/preprocess_agent/agent.py` | [문서](app/dialogue/preprocess_agent/agent.md) |
| `app/dialogue/preprocess_agent/approval_materials.py` | [문서](app/dialogue/preprocess_agent/approval_materials.md) |
| `app/dialogue/preprocess_agent/free_questions.py` | [문서](app/dialogue/preprocess_agent/free_questions.md) |
| `app/dialogue/preprocess_agent/planning.py` | [문서](app/dialogue/preprocess_agent/planning.md) |
| `app/dialogue/preprocess_agent/prompt.py` | [문서](app/dialogue/preprocess_agent/prompt.md) |
| `app/dialogue/preprocess_agent/question_search.py` | [공개 진술 벡터 검색](../app/dialogue/preprocess_agent/question_search.py) |

## 생성 에이전트

| 소스 파일 | 설명 |
|---|---|
| `app/dialogue/inference_agent/__init__.py` | [문서](app/dialogue/inference_agent/__init__.md) |
| `app/dialogue/inference_agent/agent.py` | [문서](app/dialogue/inference_agent/agent.md) |

## 검증 에이전트

| 소스 파일 | 설명 |
|---|---|
| `app/dialogue/validation_agent_v1/__init__.py` | [문서](app/dialogue/validation_agent/__init__.md) |
| `app/dialogue/validation_agent_v1/agent.py` | [문서](app/dialogue/validation_agent/agent.md) |
| `app/dialogue/validation_agent_v1/critical_facts.py` | [문서](app/dialogue/validation_agent/critical_facts.md) |
| `app/dialogue/validation_agent_v1/evidence_checks.py` | [문서](app/dialogue/validation_agent/evidence_checks.md) |
| `app/dialogue/validation_agent_v1/meaning_guards.py` | [문서](app/dialogue/validation_agent/meaning_guards.md) |
| `app/dialogue/validation_agent_v1/output.py` | [문서](app/dialogue/validation_agent/output.md) |
| `app/dialogue/validation_agent_v1/prompt.py` | [문서](app/dialogue/validation_agent/prompt.md) |
| `app/dialogue/validation_agent_v1/report_policy.py` | [문서](app/dialogue/validation_agent/report_policy.md) |
| `app/dialogue/validation_agent_v1/semantic_verification.py` | [문서](app/dialogue/validation_agent/semantic_verification.md) |
| `app/dialogue/validation_agent_v1/verification.py` | [문서](app/dialogue/validation_agent/verification.md) |
| `app/dialogue/validation_agent_v1/verification_prompting.py` | [문서](app/dialogue/validation_agent/verification_prompting.md) |
| `app/dialogue/validation_agent_v1/verification_reports.py` | [문서](app/dialogue/validation_agent/verification_reports.md) |
| `app/dialogue/validation_agent_v1/verification_units.py` | [문서](app/dialogue/validation_agent/verification_units.md) |

## 앱 시작과 공용 코드

| 소스 파일 | 설명 |
|---|---|
| `app/__init__.py` | [문서](app/__init__.md) |
| `app/bootstrap.py` | [문서](app/bootstrap.md) |
| `app/config.py` | [문서](app/config.md) |
| `app/dependencies.py` | [문서](app/dependencies.md) |
| `app/dialogue/__init__.py` | [문서](app/dialogue/__init__.md) |
| `app/dialogue/diagnostics.py` | [문서](app/dialogue/diagnostics.md) |
| `app/dialogue/interrogation_graph.py` | [문서](app/dialogue/interrogation_graph.md) |
| `app/dialogue/local_model.py` | [문서](app/dialogue/local_model.md) |
| `app/dialogue/model_loading.py` | [문서](app/dialogue/model_loading.md) |
| `app/dialogue/preprocess_agent/rag/__init__.py` | [문서](app/dialogue/preprocess_agent/rag/__init__.md) |
| `app/dialogue/reply_validation.py` | [문서](app/dialogue/reply_validation.md) |
| `app/dialogue/schemas.py` | [문서](app/dialogue/schemas.md) |
| `app/dialogue/state.py` | [문서](app/dialogue/state.md) |
| `app/main.py` | [문서](app/main.md) |

## 사건 데이터와 API

| 소스 파일 | 설명 |
|---|---|
| `app/cases/__init__.py` | [문서](app/cases/__init__.md) |
| `app/cases/catalog.py` | [문서](app/cases/catalog.md) |
| `app/cases/routes.py` | [문서](app/cases/routes.md) |

## 수사 진행과 저장

| 소스 파일 | 설명 |
|---|---|
| `app/investigation/__init__.py` | [문서](app/investigation/__init__.md) |
| `app/investigation/rules/accusation.py` | [문서](app/investigation/rules/accusation.md) |
| `app/investigation/rules/engine.py` | [문서](app/investigation/rules/engine.md) |
| `app/investigation/rules/evidence.py` | [문서](app/investigation/rules/evidence.md) |
| `app/investigation/views/material_display.py` | [문서](app/investigation/views/material_display.md) |
| `app/investigation/api/material_routes.py` | [문서](app/investigation/api/material_routes.md) |
| `app/investigation/views/presentation.py` | [문서](app/investigation/views/presentation.md) |
| `app/investigation/persistence/repository.py` | [문서](app/investigation/persistence/repository.md) |
| `app/investigation/views/result_display.py` | [문서](app/investigation/views/result_display.md) |
| `app/investigation/api/routes.py` | [문서](app/investigation/api/routes.md) |
| `app/investigation/api/schemas.py` | [문서](app/investigation/api/schemas.md) |
| `app/investigation/views/screen_views.py` | [문서](app/investigation/views/screen_views.md) |
| `app/investigation/service.py` | [문서](app/investigation/service.md) |
| `app/investigation/persistence/storage.py` | [문서](app/investigation/persistence/storage.md) |
| `app/investigation/rules/testimony.py` | [문서](app/investigation/rules/testimony.md) |
| `app/investigation/views/timeline.py` | [문서](app/investigation/views/timeline.md) |
| `app/investigation/api/view_routes.py` | [문서](app/investigation/api/view_routes.md) |

## 실서버 검사 도구

| 소스 파일 | 설명 |
|---|---|
| `scripts/__init__.py` | [문서](scripts/__init__.md) |
| `scripts/live_dialogue/__init__.py` | [문서](scripts/live_dialogue/__init__.md) |
| `scripts/live_dialogue/case_runner.py` | [문서](scripts/live_dialogue/case_runner.md) |
| `scripts/live_dialogue/definitions.py` | [문서](scripts/live_dialogue/definitions.md) |
| `scripts/live_dialogue/errors.py` | [문서](scripts/live_dialogue/errors.md) |
| `scripts/live_dialogue/example_reports.py` | [문서](scripts/live_dialogue/example_reports.md) |
| `scripts/live_dialogue/examples.py` | [문서](scripts/live_dialogue/examples.md) |
| `scripts/live_dialogue/tester.py` | [문서](scripts/live_dialogue/tester.md) |
| `scripts/live_dialogue/traces.py` | [문서](scripts/live_dialogue/traces.md) |
| `scripts/live_dialogue/transport.py` | [문서](scripts/live_dialogue/transport.md) |
| `scripts/run_130_live_examples.py` | [문서](scripts/run_130_live_examples.md) |
| `scripts/test_llm_api_live.py` | [문서](scripts/test_llm_api_live.md) |

## 회귀 테스트

| 소스 파일 | 설명 |
|---|---|
| `tests/__init__.py` | [문서](tests/__init__.md) |
| `tests/cases/__init__.py` | [문서](tests/cases/__init__.md) |
| `tests/cases/test_catalog.py` | [문서](tests/cases/test_catalog.md) |
| `tests/conftest.py` | [문서](tests/conftest.md) |
| `tests/dialogue/__init__.py` | [문서](tests/dialogue/__init__.md) |
| `tests/dialogue/models.py` | [문서](tests/dialogue/models.md) |
| `tests/dialogue/test_free_question_recovery.py` | [문서](tests/dialogue/test_free_question_recovery.md) |
| `tests/dialogue/inference_agent/test_paraphrase_generation.py` | [문서](tests/dialogue/test_paraphrase_generation.md) |
| `tests/dialogue/test_reply_availability.py` | [문서](tests/dialogue/test_reply_availability.md) |
| `tests/dialogue/test_question_search.py` | [자유 질문 검색 검사](../tests/dialogue/test_question_search.py) |
| `tests/dialogue/test_runtime.py` | [문서](tests/dialogue/test_runtime.md) |
| `tests/dialogue/validation_agent/test_verification_reports.py` | [문서](tests/dialogue/test_verification_reports.md) |
| `tests/investigation/__init__.py` | [문서](tests/investigation/__init__.md) |
| `tests/investigation/data_helpers.py` | [문서](tests/investigation/data_helpers.md) |
| `tests/investigation/player.py` | [문서](tests/investigation/player.md) |
| `tests/investigation/test_api_routes.py` | [문서](tests/investigation/test_api_routes.md) |
| `tests/investigation/test_game_progress.py` | [문서](tests/investigation/test_game_progress.md) |
| `tests/investigation/test_invalid_actions.py` | [문서](tests/investigation/test_invalid_actions.md) |
| `tests/investigation/test_minimum_success_route.py` | [문서](tests/investigation/test_minimum_success_route.md) |
| `tests/investigation/test_open_accusation.py` | [문서](tests/investigation/test_open_accusation.md) |
| `tests/investigation/test_screen_views.py` | [문서](tests/investigation/test_screen_views.md) |
| `tests/dialogue/test_runner.py` | [문서](tests/live_dialogue/test_runner.md) |
| `tests/dialogue/test_trace_and_timeout.py` | [문서](tests/live_dialogue/test_trace_and_timeout.md) |
| `tests/test_code_conventions.py` | [문서](tests/test_code_conventions.md) |

## 호환 경로

이전 import를 연결하는 파일이다. 새 구현을 읽으려면 각 페이지의 실제 구현 링크를 따른다.
| 소스 파일 | 설명 |
|---|---|
| `app/dialogue/agents.py` | [문서](app/dialogue/agents.md) |
