# 검증 에이전트

[에이전트 목차](../README.md) · 이전: [생성](../생성/README.md)

검증 에이전트는 후보 대사를 확인하고 통과·새 대사 생성·실패 처리 중 하나를 결정한다. 형식 검사는 코드로 수행하고, 의미 검사는 같은 모델을 검토 역할로 별도 호출한다.

## 시작 메서드

```python
async def validation_agent(self, state: InterrogationState) -> dict:
    ...
```

담당: `ValidationAgent.validation_agent` — [실제 코드](../../../app/dialogue/validation_agent_v1/agent.py) · [코드 참조](../../코드참조/app/dialogue/validation_agent/agent.md)

- `state`: 후보 원문, 생성 횟수와 실행 오류가 담긴 작업 기록
- 반환값: 최종 `response` 또는 재생성 여부와 거절 코드를 담은 딕셔너리

## 1. 실행 오류와 형식 검사

생성 실행 오류가 있으면 바로 실패 처리한다. 정상 출력은 `ReplyOutput.parse`에서 평문·JSON 형식, 길이, 선택적으로 신고한 사실 ID의 승인 범위와 중복을 검사한다.

이어 질문자와 행위자가 뒤바뀐 오류를 확인한다. 승인 사실이 없는 요청은 정확한 중립 대사와 빈 사실 ID인지 검사하고 `fixed`로 종료한다. 이 경로에서는 생성·검증 모델을 모두 호출하지 않는다.

[출력 처리 코드](../../../app/dialogue/validation_agent_v1/output.py)

## 2. 후보 전체의 중요 의미 검사

```python
async def verify(
    self, request: CharacterReplyRequest, response: CharacterReplyResponse
) -> CharacterReplyResponse:
    ...
```

담당: `SemanticVerifier.verify` — [실제 코드](../../../app/dialogue/validation_agent_v1/verification.py)

먼저 `critical_claim_error`가 승인되지 않은 수량·시각·행동 연결이나 필수 의미 누락 등 알려진 오류를 확인한다. 제한된 정규식과 표현 사전이므로 일반적인 한국어 의미 전체를 판정하지는 않는다.

## 3. 별도 모델에 의미 보고서 요청

`VerificationReporter.request_report`는 승인 사실을 문장별 항목으로 나누고, 설정된 배치 크기로 검증 모델을 호출한다. 전체 승인 계획은 각 배치에 유지하고, 이번에 검사할 항목만 나눈다.

검증 프롬프트는 승인 문장, 후보 문장의 실제 번호, 인물 설정과 최근 대화를 전달한다. 모델에는 `purpose="verification"`을 지정하고 샘플링하지 않는다.

[보고서 요청 코드](../../../app/dialogue/validation_agent_v1/verification_reports.py) · [검증 프롬프트](../../../app/dialogue/validation_agent_v1/prompt.py)

## 4. 보고서의 근거도 검사

`check_report_evidence`는 다음을 확인한다.

- 요청한 모든 승인 항목이 정확히 한 번씩 포함되었는가?
- 근거 문장 번호가 실제 후보에 존재하고 중복되지 않는가?
- 포함되었다고 판정하면 근거가 있고, 포함되지 않았다면 근거 번호가 없는가?
- 선택한 실제 근거 문장에 수량·시각·관찰 한계 등 중요한 의미가 남아 있는가?

한 사실에 여러 승인 문장이 있으면 모든 문장이 확인되어야 그 사실의 ID를 인정한다.

[근거 검사 코드](../../../app/dialogue/validation_agent_v1/evidence_checks.py)

## 5. 의미 거절과 최종 사실 ID

[report_policy.py](../../../app/dialogue/validation_agent_v1/report_policy.py)의 `reject_semantic_errors`는 불확실성, 모순, 승인되지 않은 추가 주장, 과거 대화 충돌, 인물 설정 불일치를 거절한다. 여러 배치의 결과는 어느 하나의 부정 판정도 긍정 판정으로 덮어쓰지 않고 합친다.

필수 사실 전체가 포함되었는지 확인한 뒤 최종 `used_fact_ids`를 검증 결과로 다시 구성한다. 생성자가 “이 사실을 사용했다”고 신고한 목록을 그대로 믿지 않는다.

생성 대사에는 원문을 그대로 복사하도록 요구하지 않는다. 의미 검증을 통과한 대사를 최종 계약 검사로 확인한다.

## 6. 재시도는 두 종류

| 문제 | 다시 하는 일 | 담당 |
|---|---|---|
| 대사에 사실 누락·모순 등이 탐지됨 | 허용 횟수가 남으면 새 대사 생성 | 검증 에이전트 → 그래프 → 생성 에이전트 |
| 보고서 JSON·스키마·검사 항목·근거 번호 오류 | 같은 후보의 보고서만 재요청 | `VerificationReporter` |

의미상 거절을 동일 후보로 계속 검사해 통과시키려 하지 않는다. 보고서 형식 오류의 상한이 소진되면 대사 재생성으로 넘어가지 않고 최종 실패 처리한다. 모델 실행 오류와 시간 초과도 별도 실패 경로를 따른다.

기본 생성 상한 2회는 최초 생성까지 포함한다. 보고서 요청 상한 2회는 배치별 값이다. 모델 호출 총 횟수는 배치 수와 실패 상황에 따라 달라진다.

실패 시 승인 원문 복구 여부는 [응답·복구 정책](../응답과_복구_정책.md)을 확인한다. 규칙과 모델 검사를 결합해도 검증 통과가 사실성의 완전한 보증은 아니다.
