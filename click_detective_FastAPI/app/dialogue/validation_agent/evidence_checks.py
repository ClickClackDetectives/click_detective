"""의미 검증 보고서의 항목과 실제 근거 문장을 검사한다."""

from ..diagnostics import trace_event
from ..schemas import CharacterReplyRequest
from ..state import OutputRejected
from .critical_facts import critical_evidence_error
from .semantic_verification import SemanticReport, candidate_sentences
from .verification_units import build_verification_units


def check_report_evidence(
    report: SemanticReport,
    request: CharacterReplyRequest,
    reply: str,
    units=None,
) -> set[str]:
    """판정 자체에 앞서 항목의 완전성과 실제 원문 인용을 검사한다.

    Args:
        report (SemanticReport): 검사 결과와 실행 기록을 담은 보고서.
        request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
        reply (str): 의미를 검사하거나 문장으로 나눌 후보 대사.
        units: 이번에 검사할 승인 문장 목록. None이면 전체를 검사한다.

    Returns:
        set[str]: 모든 문장 항목이 근거로 확인된 사실 ID 집합.
    """
    all_units = build_verification_units(request)
    if units is None:
        units = all_units
    expected = set()
    for unit in units:
        expected.add(int(unit.id.removeprefix("unit-")))
    checked = []
    for index, _, _ in report.checks:
        checked.append(index)
    if len(checked) != len(set(checked)) or set(checked) != expected:
        if len(checked) != len(set(checked)):
            reason = "duplicate_unit_indexes"
        else:
            reason = "unit_index_set_mismatch"
        trace_event(
            "verification_unit_issue",
            reason=reason,
            expected_count=len(expected),
            actual_count=len(checked),
        )
        raise OutputRejected("verification_fact_ids_mismatch", reason)
    sentences = candidate_sentences(reply)
    valid_ids = set()
    for part in sentences:
        valid_ids.add(part.id)
    supported_ids = set()
    for index, supported, evidence in report.checks:
        reason = ""
        if len(evidence) != len(set(evidence)):
            reason = "duplicate_evidence_ids"
        elif not set(evidence).issubset(valid_ids):
            reason = "out_of_range_evidence_id"
        elif supported and not evidence:
            reason = "missing_positive_evidence"
        elif not supported and evidence:
            reason = "unexpected_negative_evidence"
        if reason:
            trace_event(
                "verification_evidence_issue",
                reason=reason,
                unit_index=index,
                candidate_sentence_count=len(sentences),
            )
            raise OutputRejected("verification_evidence_mismatch", reason)
        if supported:
            evidence_text = " ".join(
                sentences[part_id].text for part_id in sorted(evidence)
            )
            guard = critical_evidence_error(all_units[index].text, evidence_text)
            if guard:
                raise OutputRejected(guard)
            supported_ids.add(index)
    supported_facts = set()
    for fact in request.allowed_facts:
        fact_has_units = False
        all_units_supported = True
        for unit in units:
            if unit.fact_id != fact.id:
                continue
            fact_has_units = True
            unit_index = int(unit.id.removeprefix("unit-"))
            if unit_index not in supported_ids:
                all_units_supported = False
        if fact_has_units and all_units_supported:
            supported_facts.add(fact.id)
    return supported_facts
