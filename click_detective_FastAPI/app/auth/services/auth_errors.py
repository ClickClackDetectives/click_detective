"""인증 경계에서 일관된 오류 응답을 정의한다."""

from fastapi import HTTPException


def auth_error(status, code, message):
    """브라우저 중계에 전달할 인증 오류를 만든다.

    Args:
        status: 사용할 HTTP 상태 코드.
        code: 클라이언트가 흐름을 분기하는 오류 코드.
        message: 입력값을 제외한 공개 오류 문구.

    Returns:
        HTTPException: API 응답으로 처리할 예외.
    """
    return HTTPException(status, {"code": code, "message": message})


def require_expected_account(user_id, expected_user):
    """이전 탭의 요청이 현재 브라우저의 다른 계정을 바꾸지 못하게 한다.

    Args:
        user_id: 토큰 검증 또는 저장소 조회로 얻은 실제 계정 ID.
        expected_user: 탭이 작업하려던 계정 ID 또는 지정하지 않았으면 None.

    Returns:
        None: 대상이 일치하거나 지정하지 않았을 때 계속 진행한다.
    """
    if expected_user is not None and str(user_id) != expected_user:
        raise auth_error(409, "ACCOUNT_CHANGED", "로그인 계정이 변경되었습니다.")
