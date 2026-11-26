# 후보 대사를 승인 근거와 대조하기

local 그래프의 `ValidationAgent`는 후보 대사의 출력 형식을 확인하고 문장별로 승인 근거를 찾습니다. 전처리에서 생성 프롬프트에 쓴 `verification_units`를 같은 요청의 검증에 사용합니다. [검증 구현](../../../app/dialogue/services/validation_agent/workflow/dialogue_validation_agent.py)

1. 후보를 문장으로 나누고 직접 일치와 문장 임베딩 유사도로 승인 단위를 찾습니다.
2. 규칙만으로 확정하기 어려운 문장은 같은 로컬 모델에 `purpose="verification"`으로 보냅니다. `CLICK_VERIFICATION_BATCH_SIZE`는 한 번에 검사할 후보 수를 제어합니다.
3. 통과한 문장을 원래 순서로 모으고 연결된 사실 ID를 기록합니다. 대사와 기록 확정에 필요한 조건은 판정 정책에서 확인합니다. [판정 정책](../../../app/dialogue/services/validation_agent/policy/dialogue_validation_policy.py)

`stop`, `partial`, `neutral`은 필수 사실을 모두 전달했는지, 일부가 누락됐는지, 중립 응답을 반환했는지를 확인하는 데 사용합니다. [응답과 복구 정책](../응답과_복구_정책.md)

문장 임베딩의 모델과 장치는 `CLICK_VALIDATION_EMBEDDING_MODEL`, `CLICK_VALIDATION_EMBEDDING_DEVICE`로 설정합니다. 실서버 진단의 `verification_policy`, `verification`, `validation_outcome`을 보면 정책 실행, 모델 호출, 판정 결과를 추적할 수 있습니다. [실서버 검사](../../테스트/실서버_LLM_검사.md)
