# 검증 에이전트

검증은 하나의 구현을 사용한다. 생성 프롬프트에 사용한 승인 문장 단위와 모델이 반환한 후보 대사를 비교한다. [검증 에이전트](../../../app/dialogue/services/validation_agent/workflow/dialogue_validation_agent.py)

1. 출력 형식과 사실 ID를 검사하고 후보 대사를 문장별로 나눈다.
2. 문장 임베딩 유사도와 직접 일치 규칙으로 후보별 승인 단위를 고른다.
3. 규칙으로 확정하기 어려운 문장만 같은 로컬 모델에 검증 목적으로 보낸다. 한 번의 검증 배치에는 `CLICK_VERIFICATION_BATCH_SIZE`만큼 후보를 넣는다.
4. 검증된 문장을 원래 순서대로 모아 응답하고, 승인 문장과 연결된 사실 ID를 기록한다.

승인 사실이 없는 질문에서는 인물의 공개 발언과 최근 대화를 근거로 공개 범위를 검사한다. 질문자가 제시한 전제는 공개 근거로 사용하지 않는다. 새 쟁점은 승인 계획의 핵심 문장이 검증되었을 때만 기록한다.

검증에 통과하면 `stop`, 필수 사실 일부를 전달하면 `partial`, 승인된 답을 구성할 수 없으면 `neutral`을 반환한다. [판정 정책](../../../app/dialogue/services/validation_agent/policy/dialogue_validation_policy.py) · [응답과 복구](../응답과_복구_정책.md)

## 설정과 진단

문장 임베딩은 SentenceTransformer를 사용한다. 모델 위치와 실행 장치는 `CLICK_VALIDATION_EMBEDDING_MODEL`과 `CLICK_VALIDATION_EMBEDDING_DEVICE`로 설정한다. 진단의 `verification_policy`는 정책 실행 시간, `verification`은 검증 모델 호출, `validation_outcome`은 전달·보류된 사실 ID를 기록한다. [실서버 검사](../../테스트/실서버_LLM_검사.md)
