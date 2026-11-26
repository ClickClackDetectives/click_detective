# 생성 에이전트

[에이전트 목차](../README.md) · 이전: [전처리](../전처리/README.md) · 다음: [검증](../검증/README.md)

생성 노드는 전처리 결과로 후보 대사를 만든다. fixture는 고정 응답을 사용하고 local은 같은 프로세스의 로컬 모델을 호출한다.

## 시작 메서드

```python
async def inference_agent(self, state: InterrogationState) -> dict:
    ...
```

담당: `InferenceAgent.inference_agent` — [실제 코드](../../../app/dialogue/services/inference_agent/dialogue_inference_agent.py) · [코드 참조](../../코드참조/app/dialogue/services/inference_agent/dialogue_inference_agent.md)

- `state`: 질문, 생성용 프롬프트와 이전 거절 코드가 들어 있는 작업 기록
- 반환값: 시도 횟수와 후보 원문 또는 실행 오류 상태를 담은 딕셔너리

## 동작 순서

1. 승인 사실이 없으면 모델을 호출하지 않는다. `assemble_reply`로 중립 대사를 준비한다.
2. 승인 사실이 있으면 전처리가 만든 `messages`를 복사한다.
4. `attempt`를 1 증가시키고 모델에 `purpose="dialogue"`로 요청한다.
5. 모델 원문을 `raw_output`에 담아 검증 단계로 넘긴다.


## 생성 목적과 검증 목적의 차이

같은 모델을 사용하되 대사 생성에는 기본적으로 샘플링을 적용하고, 검증에는 greedy 방식을 사용한다.

| 설정 | 기본값 | 뜻 |
|---|---|---|
| `dialogue_temperature` | 0.65 | 표현 선택의 다양성. 0이면 샘플링하지 않음 |
| `dialogue_top_p` | 0.9 | 다음 토큰 선택 후보의 누적 확률 범위 |
| `dialogue_repetition_penalty` | 1.05 | 같은 표현 반복 억제 |

샘플링은 문장 표현의 선택 방식이다. 필수 항목 하나를 대사 한 문장으로 쓰고, 항목 사이의 문장 경계를 유지한다. 새로운 사건 사실을 추가해도 된다는 권한이 아니다. 반드시 승인 의미를 보존해야 한다.

## 평문 대사와 API JSON

기본 `generation_output_format="text"`에서 모델은 대사 원문을 출력한다. API의 최종 응답 JSON은 서버가 만든다. 내부 모델 출력이 JSON이어야만 API가 JSON을 반환하는 것은 아니다.

내부 `json` 모드는 모델이 `{"reply":"대사"}` 형식으로 출력하도록 요청한다. 두 형식 모두 이후 검증을 거친다.

## 실행 오류

| 상황 | 생성 단계 처리 |
|---|---|
| 입력 토큰 한도 초과 | HTTP 422 발생 |
| 모델 실행 시간 초과 | `error_status=504` |
| 모델 실행 오류 | `error_status=502` |

오류 상태는 검증 단계의 최종 실패 처리로 넘긴다. 그래프 밖으로 전달된 예외도 서비스 복구 설정에 따라 중립 응답으로 처리될 수 있다.

모델 실제 실행과 GPU 잠금은 [공용 모델](../공용_모델.md), 최종 처리 조건은 [응답·복구 정책](../응답과_복구_정책.md)에서 확인한다.
