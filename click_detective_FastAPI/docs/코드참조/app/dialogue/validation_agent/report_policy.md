# `app/dialogue/validation_agent_v1/report_policy.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/validation_agent_v1/report_policy.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 71줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

검증 보고서의 거절 조건과 배치 결과 통합 규칙을 정의한다.

## 함께 읽을 코드

- [app/dialogue/state.py](../state.md)
- [app/dialogue/validation_agent_v1/semantic_verification.py](semantic_verification.md)

## `reject_semantic_errors`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/report_policy.py#L16)

```python
def reject_semantic_errors(report: SemanticReport) -> None:
    ...
```

의미상 거절 조건이 있으면 첫 오류 코드로 후보를 거절한다.

**파라미터**

- report: 모델이 제출한 검증 보고서.

**반환값**

None: 모든 조건을 통과하면 정상 종료한다. 실패하면 OutputRejected를 낸다.

## `combine_reports`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/report_policy.py#L37)

```python
def combine_reports(reports: list[SemanticReport]) -> SemanticReport:
    ...
```

각 배치의 부정 판정을 유지하며 전체 보고서로 합친다.

**파라미터**

- reports: 승인 문장을 나누어 검사한 배치별 보고서.

**반환값**

SemanticReport: 전체 항목과 가장 보수적인 일관성·모순 판정을 담은 보고서.
