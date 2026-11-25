"""Next.js 서버가 사용하는 인증 HTTP 계약을 제공한다."""

from fastapi import APIRouter, Depends, Request

from app.dependencies import authenticate, service

from .contracts import Account, Credentials, DeleteAccount, TokenPair
from .errors import auth_error, require_expected_account

router = APIRouter(prefix="/auth", tags=["계정"], dependencies=[Depends(authenticate)])


def auth_service(request: Request):
    """FastAPI 앱의 인증 서비스가 준비됐는지 확인한다.

    Args:
        request: 인증 서비스를 보관하는 FastAPI 앱의 요청.

    Returns:
        AuthService: 준비된 인증 서비스 또는 미설정 오류.
    """
    auth = getattr(request.app.state, "auth", None)
    if auth is None:
        raise auth_error(
            503, "AUTH_DISABLED", "서버에 계정 인증이 설정되지 않았습니다."
        )
    return auth


def current_user(request: Request):
    """서버 중계가 제공한 접근 토큰과 기대 계정을 검증한다.

    Args:
        request: 서버 중계의 인증 헤더가 들어있는 요청.

    Returns:
        dict: 인증된 계정 ID와 이메일.
    """
    token = request.headers.get("X-Access-Token", "")
    user = auth_service(request).me(token)
    expected_user = request.headers.get("X-Expected-User-Id")
    require_expected_account(user["id"], expected_user)
    return user


def auth_peer(request: Request):
    """인증 요청 제한에 사용할 신뢰된 연결 상대 주소를 고른다.

    Args:
        request: 서버 중계에서 온 FastAPI 요청.

    Returns:
        str: 연결 상대 주소 또는 알 수 없는 주소의 공통 값.
    """
    return request.client.host if request.client else "unknown"


@router.post("/signup", status_code=201, response_model=Account)
def signup(command: Credentials, request: Request):
    """신규 계정을 등록하고 공개 계정 정보를 반환한다.

    Args:
        command: 가입 이메일과 비밀번호.
        request: 인증 서비스에 접근할 FastAPI 요청.

    Returns:
        dict: 인증 토큰을 발급하지 않는 공개 계정 요약.
    """
    auth = auth_service(request)
    auth.throttle("signup", command.email, auth_peer(request))
    return auth.signup(command.email, command.password.get_secret_value())


@router.post("/login", response_model=TokenPair)
def login(command: Credentials, request: Request):
    """사용자 자격 증명으로 새 로그인 세션을 연다.

    Args:
        command: 로그인 이메일과 비밀번호.
        request: 인증 서비스에 접근할 FastAPI 요청.

    Returns:
        dict: Next.js 서버가 쿠키로 옮길 토큰과 공개 계정 정보.
    """
    auth = auth_service(request)
    auth.throttle("login", command.email, auth_peer(request))
    return auth.login(command.email, command.password.get_secret_value())


@router.get("/me", response_model=Account)
def me(request: Request):
    """현재 로그인 계정의 공개 정보를 조회한다.

    Args:
        request: 서버 중계의 접근 토큰이 있는 요청.

    Returns:
        dict: 공개 계정 ID와 정규화된 이메일.
    """
    return current_user(request)


@router.post("/refresh", response_model=TokenPair)
def refresh(request: Request):
    """서버 중계의 갱신 토큰을 회전한다.

    Args:
        request: 갱신 토큰 헤더를 읽을 FastAPI 요청.

    Returns:
        dict: 새 토큰 쌍과 각 만료 시각 및 공개 계정 정보.
    """
    return auth_service(request).refresh(
        request.headers.get("X-Refresh-Token", ""),
        expected_user=request.headers.get("X-Expected-User-Id"),
    )


@router.post("/logout")
def logout(request: Request):
    """현재 로그인 세션을 폐기한다.

    Args:
        request: 접근 또는 갱신 토큰을 읽을 FastAPI 요청.

    Returns:
        dict: 저장소에서 세션 폐기를 확인한 결과.
    """
    refresh_token = request.headers.get("X-Refresh-Token", "")
    access_token = request.headers.get("X-Access-Token", "")
    auth_service(request).logout(
        refresh_token,
        access_token,
        expected_user=request.headers.get("X-Expected-User-Id"),
    )
    return {"ok": True}


@router.post("/delete", status_code=202)
def delete_account(command: DeleteAccount, request: Request):
    """현재 세션의 계정을 비밀번호 확인 후 탈퇴 대기 상태로 바꾼다.

    Args:
        command: 계정 삭제에 필요한 현재 비밀번호.
        request: 인증 세션과 구성된 수사 저장소에 접근할 요청.

    Returns:
        dict: 모든 세션의 폐기와 작업 등록을 확인한 결과.
    """
    user = current_user(request)
    if not hasattr(service(request).repository, "delete_owned"):
        raise auth_error(
            503, "DELETION_DISABLED", "계정 데이터 정리 기능이 설정되지 않았습니다."
        )
    auth = auth_service(request)
    auth.throttle("delete", user["email"], auth_peer(request))
    auth.delete(user["id"], command.password.get_secret_value())
    return {"ok": True}
