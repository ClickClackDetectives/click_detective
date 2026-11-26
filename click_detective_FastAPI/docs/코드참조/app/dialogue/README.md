# 대화 생성과 검증

[코드 참조 홈](../../README.md)

승인 문맥을 검색·생성·검증 그래프로 처리하고 중립 응답과 복구 정책을 적용한다.

## 패키지

- [`__init__.py`](__init__.md)

## HTTP 컨트롤러

- [`controllers/dialogue_agent_test_controller.py`](controllers/dialogue_agent_test_controller.md)

## 서비스와 규칙

- [`services/inference_agent/__init__.py`](services/inference_agent/__init__.md)
- [`services/inference_agent/dialogue_inference_agent.py`](services/inference_agent/dialogue_inference_agent.md)
- [`services/preprocess_agent/__init__.py`](services/preprocess_agent/__init__.md)
- [`services/preprocess_agent/dialogue_preprocess_agent.py`](services/preprocess_agent/dialogue_preprocess_agent.md)
- [`services/preprocess_agent/dialogue_preprocess_prompt.py`](services/preprocess_agent/dialogue_preprocess_prompt.md)
- [`services/preprocess_agent/rag/__init__.py`](services/preprocess_agent/rag/__init__.md)

### 심문 그래프와 응답

- [`dialogue_interrogation_graph.py`](services/reply/dialogue_interrogation_graph.md)
- [`dialogue_reply_service.py`](services/reply/dialogue_reply_service.md)
- [`dialogue_reply_validation.py`](services/reply/dialogue_reply_validation.md)

### 로컬 모델

- [`dialogue_local_model.py`](services/model/dialogue_local_model.md)
- [`dialogue_model_loading.py`](services/model/dialogue_model_loading.md)

### 실행 진단

- [`dialogue_diagnostics.py`](services/diagnostics/dialogue_diagnostics.md)

### 텍스트 비교

- [`dialogue_text_relevance.py`](services/text/dialogue_text_relevance.md)

### 검증 에이전트

#### 검증 흐름

- [`dialogue_validation_agent.py`](services/validation_agent/workflow/dialogue_validation_agent.md)

#### 규칙과 모델 판정

- [`dialogue_rule_policy.py`](services/validation_agent/policy/dialogue_rule_policy.md)
- [`dialogue_validation_policy.py`](services/validation_agent/policy/dialogue_validation_policy.md)

#### 승인 근거 대조

- [`dialogue_critical_facts.py`](services/validation_agent/evidence/dialogue_critical_facts.md)
- [`dialogue_meaning_guards.py`](services/validation_agent/evidence/dialogue_meaning_guards.md)
- [`dialogue_rules.py`](services/validation_agent/evidence/dialogue_rules.md)

#### 문장 단위 처리

- [`dialogue_semantic_verification.py`](services/validation_agent/sentences/dialogue_semantic_verification.md)
- [`dialogue_verification_units.py`](services/validation_agent/sentences/dialogue_verification_units.md)

#### 출력과 중립 응답

- [`dialogue_neutral.py`](services/validation_agent/output/dialogue_neutral.md)
- [`dialogue_output.py`](services/validation_agent/output/dialogue_output.md)
- [`dialogue_output_rejected.py`](services/validation_agent/output/dialogue_output_rejected.md)

## 데이터 계약

- [`dto/dialogue_graph_state.py`](dto/dialogue_graph_state.md)
- [`dto/dialogue_reply_dto.py`](dto/dialogue_reply_dto.md)

## 저장소

- [`repositories/dialogue_chroma_index.py`](repositories/dialogue_chroma_index.md)
- [`repositories/dialogue_model_file_repository.py`](repositories/dialogue_model_file_repository.md)

## 의존성 조립

- [`providers/dialogue_provider.py`](providers/dialogue_provider.md)
