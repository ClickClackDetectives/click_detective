# 전처리에서 승인 문맥 만들기

1. 수사 서비스의 `Planner.prepare`가 인물, 남은 질문 수, 명시한 주제, 제시 자료의 획득 여부를 확인합니다. 자료 조건을 충족해 새 쟁점이 열리면 인정 진술을 계획에 넣습니다. [심문 계획 코드](../../../app/investigation/services/interrogation/investigation_interrogation_planner.py)
2. 자유 질문에 검색 문맥이 있으면 `PreprocessAgent.preprocess_agent`가 승인 범위 안에서 진술을 고릅니다. BM25가 켜져 있으면 E5·ChromaDB와 Kiwi BM25가 동시에 검색합니다. E5가 관련 개별 진술을 찾으면 시각 조건을 만족하고 BM25 점수가 1.25 이상인 BM25 1위 진술을 후보에 합칩니다. 가중 RRF로 개별 진술 순위를 정하고 `RAG_TOP_K`개까지 승인 사실과 수사 기록에 사용할 계획에 반영합니다. [검색 구현](../../../app/dialogue/services/preprocess_agent/rag/dialogue_fact_retriever.py)
3. 승인 사실을 문장 단위로 만들고 같은 목록으로 생성 프롬프트를 구성합니다. 검증 문장 단위가 256개를 넘으면 HTTP 422를 반환합니다. 생성 단계에는 갱신된 `request`, `messages`, `verification_units`를 넘깁니다. [전처리 구현](../../../app/dialogue/services/preprocess_agent/dialogue_preprocess_agent.py) · [프롬프트 구현](../../../app/dialogue/services/preprocess_agent/dialogue_preprocess_prompt.py)

명시한 주제와 자료로 열린 인정 진술은 수사 규칙에서 선택합니다. 검색 결과가 비면 승인 사실이 없는 문맥이 이어집니다. [검색 설정](../검색과_표현_자유도.md) · [생성 단계](../생성/README.md)
