"""검증 보고서의 거절 조건과 배치 결과 통합 규칙을 정의한다."""

from ..state import OutputRejected
from .semantic_verification import SemanticReport

VERIFICATION_FORMAT_CODES = frozenset(
    {
        "invalid_verification_json",
        "invalid_verification_schema",
        "verification_fact_ids_mismatch",
        "verification_evidence_mismatch",
    }
)


def reject_semantic_errors(report: SemanticReport) -> None:
    """의미상 거절 조건이 있으면 첫 오류 코드로 후보를 거절한다.

    Args:
        report: 모델이 제출한 검증 보고서.

    Returns:
        None: 모든 조건을 통과하면 정상 종료한다. 실패하면 OutputRejected를 낸다.
    """
    if report.uncertain:
        raise OutputRejected("semantic_uncertain")
    if report.has_contradiction:
        raise OutputRejected("contradictory_reply")
    if report.has_unsupported_claims:
        raise OutputRejected("unsupported_claims")
    if not report.history_consistent:
        raise OutputRejected("history_conflict")
    if not report.persona_consistent:
        raise OutputRejected("persona_mismatch")


def combine_reports(reports: list[SemanticReport]) -> SemanticReport:
    """각 배치의 부정 판정을 유지하며 전체 보고서로 합친다.

    Args:
        reports: 승인 문장을 나누어 검사한 배치별 보고서.

    Returns:
        SemanticReport: 전체 항목과 가장 보수적인 일관성·모순 판정을 담은 보고서.
    """
    checks = []
    has_contradiction = False
    has_unsupported_claims = False
    history_consistent = True
    persona_consistent = True
    uncertain = False
    for report in reports:
        checks.extend(report.checks)
        if report.has_contradiction:
            has_contradiction = True
        if report.has_unsupported_claims:
            has_unsupported_claims = True
        if not report.history_consistent:
            history_consistent = False
        if not report.persona_consistent:
            persona_consistent = False
        if report.uncertain:
            uncertain = True
    return SemanticReport(
        checks=checks,
        has_contradiction=has_contradiction,
        has_unsupported_claims=has_unsupported_claims,
        history_consistent=history_consistent,
        persona_consistent=persona_consistent,
        uncertain=uncertain,
    )
