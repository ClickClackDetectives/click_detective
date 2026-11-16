"""이전 import 경로다. 실제 코드는 validation_agent/critical_facts.py에 있다."""

from .validation_agent.critical_facts import (
    CLOCK,
    COUNT,
    NATIVE_NUMBERS,
    critical_claim_error,
    critical_evidence_error,
    postponement_target,
    predicate_anchors,
    quantity_anchors,
    time_actions,
    time_anchors,
)

__all__ = [
    "quantity_anchors",
    "time_anchors",
    "time_actions",
    "postponement_target",
    "critical_claim_error",
    "critical_evidence_error",
    "predicate_anchors",
    "NATIVE_NUMBERS",
    "COUNT",
    "CLOCK",
]
