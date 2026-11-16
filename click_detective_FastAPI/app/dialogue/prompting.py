"""이전 프롬프트 import 경로를 유지한다. 실제 코드는 각 에이전트 폴더에 있다."""

from .preprocess_agent.prompt import SYSTEM_PROMPT, build_messages, normalize_question
from .validation_agent.prompt import VERIFICATION_PROMPT, build_verification_messages

__all__ = [
    "SYSTEM_PROMPT",
    "VERIFICATION_PROMPT",
    "normalize_question",
    "build_messages",
    "build_verification_messages",
]
