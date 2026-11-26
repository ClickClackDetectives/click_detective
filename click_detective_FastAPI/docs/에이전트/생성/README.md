# 승인 문맥으로 후보 대사 생성하기

`InferenceAgent.inference_agent`는 전처리가 만든 `messages`를 읽어 후보 대사를 준비합니다. fixture에서는 `assemble_reply`로 응답을 구성하고 `finish_reason="fixed"`를 반환합니다. local에서는 로컬 모델을 `purpose="dialogue"`로 호출하고 모델의 원문을 `raw_output`으로 검증 단계에 전달합니다. [생성 노드 구현](../../../app/dialogue/services/inference_agent/dialogue_inference_agent.py)

## 출력과 실행 설정

기본 출력 형식은 평문입니다. 내부 JSON 모드에서는 모델에 `{"reply":"대사"}` 형태를 요청합니다. HTTP 응답은 서버가 모델 출력과 검증 결과를 바탕으로 구성합니다.

| 환경변수 | 기본값 | 효과 |
| --- | --- | --- |
| `CLICK_DIALOGUE_TEMPERATURE` | 0.65 | 대사 표현을 샘플링하는 정도 |
| `CLICK_DIALOGUE_TOP_P` | 0.9 | 다음 토큰 후보의 누적 확률 범위 |
| `CLICK_DIALOGUE_REPETITION_PENALTY` | 1.05 | 반복 표현에 적용하는 패널티 |

입력 토큰 예산을 초과하면 HTTP 422가 발생합니다. 생성 시간 초과와 모델 실행 오류는 생성 노드에서 각각 504와 502 상태로 기록하며, 최종 응답은 그래프와 수사 서비스의 복구 정책을 따릅니다. [공용 모델](../공용_모델.md) · [검증 단계](../검증/README.md) · [응답과 복구](../응답과_복구_정책.md)
