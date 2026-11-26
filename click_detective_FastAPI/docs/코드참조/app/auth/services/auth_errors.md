# `app/auth/services/auth_errors.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/services/auth_errors.py)

인증 경계에서 일관된 오류 응답을 정의한다.

## `auth_error`

[소스 선언](../../../../../app/auth/services/auth_errors.py#L6)

```python
def auth_error(status, code, message):
    ...
```

브라우저 중계에 전달할 인증 오류를 만든다.

**인자**

- status: 사용할 HTTP 상태 코드.
- code: 클라이언트가 흐름을 분기하는 오류 코드.
- message: 입력값을 제외한 공개 오류 문구.

**반환값**

- HTTPException: API 응답으로 처리할 예외.

## `require_expected_account`

[소스 선언](../../../../../app/auth/services/auth_errors.py#L20)

```python
def require_expected_account(user_id, expected_user):
    ...
```

이전 탭의 요청이 현재 브라우저의 다른 계정을 바꾸지 못하게 한다.

**인자**

- user_id: 토큰 검증 또는 저장소 조회로 얻은 실제 계정 ID.
- expected_user: 탭이 작업하려던 계정 ID 또는 지정하지 않았으면 None.

**반환값**

- None: 대상이 일치하거나 지정하지 않았을 때 계속 진행한다.
