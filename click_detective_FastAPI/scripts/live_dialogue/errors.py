"""실서버 대화 검사 실패를 구분한다."""


class LiveTestFailure(RuntimeError):
    """HTTP 오류 또는 실제 LLM 응답 조건 불일치를 보고서에 남기기 위한 예외.

    Args:
        없음.

    Returns:
        LiveTestFailure: 위 역할을 수행하도록 생성된 객체.
    """
