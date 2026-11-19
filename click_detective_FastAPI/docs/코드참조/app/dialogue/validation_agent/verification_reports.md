# `app/dialogue/validation_agent_v1/verification_reports.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/validation_agent_v1/verification_reports.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 137줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

모델에 의미 검증 보고서를 요청하고 형식 오류만 재요청한다.

## 함께 읽을 코드

- [app/dialogue/diagnostics.py](../diagnostics.md)
- [app/dialogue/schemas.py](../schemas.md)
- [app/dialogue/state.py](../state.md)
- [app/dialogue/validation_agent_v1/evidence_checks.py](evidence_checks.md)
- [app/dialogue/validation_agent_v1/report_policy.py](report_policy.md)
- [app/dialogue/validation_agent_v1/semantic_verification.py](semantic_verification.md)
- [app/dialogue/validation_agent_v1/verification_prompting.py](verification_prompting.md)
- [app/dialogue/validation_agent_v1/verification_units.py](verification_units.md)

## `VerificationReporter`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/verification_reports.py#L22)

```python
class VerificationReporter:
    ...
```

승인 문장을 나누어 검사하고 보고서 형식 오류에 한해 재요청한다.

**파라미터**

- settings: 배치 크기와 보고서 요청 횟수 설정.
- model: 생성에 사용한 것과 같은 모델 실행 객체.

**반환값**

VerificationReporter: 의미 검증 보고서 요청을 담당하는 객체.

## `VerificationReporter.__init__`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/verification_reports.py#L33)

```python
def __init__(self, settings, model):
    ...
```

검증 호출에 사용할 설정과 모델을 보관한다.

**파라미터**

- settings: 배치 크기와 보고서 요청 횟수 설정.
- model: 검증 목적의 프롬프트를 실행할 모델.

**반환값**

None: 의존성을 보관한다.

## `VerificationReporter.request_report`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/verification_reports.py#L46)

```python
async def request_report(
    self, request: CharacterReplyRequest, reply: str
) -> tuple[SemanticReport, set[str]]:
    ...
```

모든 문장 묶음을 검사하고 전체 보고서와 확인한 사실 ID를 반환한다.

**파라미터**

- request: 공개가 승인된 사실 전체와 필수 사실 ID를 담은 요청.
- reply: 의미를 검사할 후보 대사 원문.

**반환값**

tuple[SemanticReport, set[str]]: 통합 보고서와 모든 문장이 확인된 사실 ID.

## `VerificationReporter._request_batch`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/verification_reports.py#L71)

```python
async def _request_batch(self, request, reply, batch, batch_index):
    ...
```

같은 후보를 검사하며 보고서의 형식 오류만 제한 횟수 안에서 재요청한다.

**파라미터**

- request: 원래 승인 계획이 포함된 요청.
- reply: 이번 검사 동안 변경하지 않을 후보 대사.
- batch: 이번 모델 호출에서 확인할 승인 문장 목록.
- batch_index: 진단에 기록할 0부터 시작하는 배치 번호.

**반환값**

SemanticReport: 형식·근거·의미 조건을 모두 통과한 배치 보고서.

## `VerificationReporter._parse_report`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/verification_reports.py#L116)

```python
def _parse_report(raw, request, reply, batch):
    ...
```

보고서를 파싱하고 검사 항목과 실제 근거 문장 번호를 검증한다.

**파라미터**

- raw: 검증 모델이 출력한 JSON 원문.
- request: 전체 승인 사실을 담은 요청.
- reply: 근거 문장의 번호를 확인할 후보 대사.
- batch: 보고서가 빠짐없이 확인해야 하는 승인 문장 목록.

**반환값**

SemanticReport: JSON·스키마·항목·근거 형식을 통과한 보고서.
