"""이전 import 경로다. 실제 코드는 validation_agent/semantic_verification.py에 있다."""

from .validation_agent.semantic_verification import (
    CandidateSentence,
    SemanticReport,
    candidate_sentences,
)

__all__ = ["CandidateSentence", "candidate_sentences", "SemanticReport"]
