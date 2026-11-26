"""대사 생성과 검증 과정의 안전한 실패 사유를 정의한다."""


class OutputRejected(ValueError):
    """고정 오류 코드와 안전한 하위 사유. 모델 원문·프롬프트는 담지 않는다.

    Args:
        code (str): 원문을 포함하지 않는 고정 오류 코드.
        detail (str): 오류를 구분하기 위한 추가 사유. 비밀값은 포함하지 않는다.

    Returns:
        OutputRejected: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, code: str, detail: str = "") -> None:
        """HTTP 코드는 유지하고 내부 형식 실패 원인을 별도로 추적한다.

        Args:
            code (str): 원문을 포함하지 않는 고정 오류 코드.
            detail (str): 오류를 구분하기 위한 추가 사유. 비밀값은 포함하지 않는다.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        super().__init__(code)
        self.detail = detail
