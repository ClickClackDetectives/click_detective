# `app/dialogue/validation_agent/evidence_checks.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/validation_agent/evidence_checks.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 93줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

의미 검증 보고서의 항목과 실제 근거 문장을 검사한다.

## 함께 읽을 코드

- [app/dialogue/diagnostics.py](../diagnostics.md)
- [app/dialogue/schemas.py](../schemas.md)
- [app/dialogue/state.py](../state.md)
- [app/dialogue/validation_agent/critical_facts.py](critical_facts.md)
- [app/dialogue/validation_agent/semantic_verification.py](semantic_verification.md)
- [app/dialogue/validation_agent/verification_units.py](verification_units.md)

## `check_report_evidence`

[소스 선언 위치](../../../../../app/dialogue/validation_agent/evidence_checks.py#L11)

```python
def check_report_evidence(
    report: SemanticReport,
    request: CharacterReplyRequest,
    reply: str,
    units=None,
) -> set[str]:
    ...
```

판정 자체에 앞서 항목의 완전성과 실제 원문 인용을 검사한다.

**파라미터**

- report (SemanticReport): 검사 결과와 실행 기록을 담은 보고서.
- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- reply (str): 의미를 검사하거나 문장으로 나눌 후보 대사.
- units: 이번에 검사할 승인 문장 목록. None이면 전체를 검사한다.

**반환값**

set[str]: 모든 문장 항목이 근거로 확인된 사실 ID 집합.
