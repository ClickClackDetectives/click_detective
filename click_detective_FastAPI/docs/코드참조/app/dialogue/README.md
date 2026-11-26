# 대화 그래프와 모델 코드

그래프에서 검색, 생성, 검증 호출을 따라갈 수 있습니다. 내부 검사 라우트는 모델 확인에 사용되며, 실제 심문의 공개 범위와 저장은 수사 도메인에서 처리합니다.

[그래프](services/reply/dialogue_interrogation_graph.md) · [전처리](services/preprocess_agent/dialogue_preprocess_agent.md) · [검증](services/validation_agent/workflow/dialogue_validation_agent.md) · [자유 질문 검색](../../../../app/dialogue/services/preprocess_agent/rag/dialogue_fact_retriever.py)

| 소스 폴더 | 파일별 참조 |
| --- | --- |
| `app/dialogue/` | [`__init__.py`](__init__.md) |
| `app/dialogue/controllers/` | [`dialogue_agent_test_controller.py`](controllers/dialogue_agent_test_controller.md) |
| `app/dialogue/dto/` | [`dialogue_graph_state.py`](dto/dialogue_graph_state.md) · [`dialogue_reply_dto.py`](dto/dialogue_reply_dto.md) |
| `app/dialogue/providers/` | [`dialogue_provider.py`](providers/dialogue_provider.md) |
| `app/dialogue/repositories/` | [`dialogue_chroma_index.py`](repositories/dialogue_chroma_index.md) · [`dialogue_model_file_repository.py`](repositories/dialogue_model_file_repository.md) |
| `app/dialogue/services/diagnostics/` | [`dialogue_diagnostics.py`](services/diagnostics/dialogue_diagnostics.md) |
| `app/dialogue/services/inference_agent/` | [`__init__.py`](services/inference_agent/__init__.md) · [`dialogue_inference_agent.py`](services/inference_agent/dialogue_inference_agent.md) |
| `app/dialogue/services/model/` | [`dialogue_local_model.py`](services/model/dialogue_local_model.md) · [`dialogue_model_loading.py`](services/model/dialogue_model_loading.md) |
| `app/dialogue/services/preprocess_agent/` | [`__init__.py`](services/preprocess_agent/__init__.md) · [`dialogue_preprocess_agent.py`](services/preprocess_agent/dialogue_preprocess_agent.md) · [`dialogue_preprocess_prompt.py`](services/preprocess_agent/dialogue_preprocess_prompt.md) |
| `app/dialogue/services/preprocess_agent/rag/` | [`__init__.py`](services/preprocess_agent/rag/__init__.md) |
| `app/dialogue/services/reply/` | [`dialogue_interrogation_graph.py`](services/reply/dialogue_interrogation_graph.md) · [`dialogue_reply_service.py`](services/reply/dialogue_reply_service.md) · [`dialogue_reply_validation.py`](services/reply/dialogue_reply_validation.md) |
| `app/dialogue/services/text/` | [`dialogue_text_relevance.py`](services/text/dialogue_text_relevance.md) |
| `app/dialogue/services/validation_agent/` | [`__init__.py`](services/validation_agent/__init__.md) |
| `app/dialogue/services/validation_agent/evidence/` | [`dialogue_critical_facts.py`](services/validation_agent/evidence/dialogue_critical_facts.md) · [`dialogue_meaning_guards.py`](services/validation_agent/evidence/dialogue_meaning_guards.md) · [`dialogue_rules.py`](services/validation_agent/evidence/dialogue_rules.md) |
| `app/dialogue/services/validation_agent/output/` | [`dialogue_neutral.py`](services/validation_agent/output/dialogue_neutral.md) · [`dialogue_output.py`](services/validation_agent/output/dialogue_output.md) · [`dialogue_output_rejected.py`](services/validation_agent/output/dialogue_output_rejected.md) |
| `app/dialogue/services/validation_agent/policy/` | [`dialogue_rule_policy.py`](services/validation_agent/policy/dialogue_rule_policy.md) · [`dialogue_validation_policy.py`](services/validation_agent/policy/dialogue_validation_policy.md) |
| `app/dialogue/services/validation_agent/sentences/` | [`dialogue_semantic_verification.py`](services/validation_agent/sentences/dialogue_semantic_verification.md) · [`dialogue_verification_units.py`](services/validation_agent/sentences/dialogue_verification_units.md) |
| `app/dialogue/services/validation_agent/workflow/` | [`dialogue_validation_agent.py`](services/validation_agent/workflow/dialogue_validation_agent.md) |

[FastAPI 코드 참조](../../README.md)
