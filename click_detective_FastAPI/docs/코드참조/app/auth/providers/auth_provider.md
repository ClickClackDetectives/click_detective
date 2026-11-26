# `app/auth/providers/auth_provider.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/providers/auth_provider.py)

앱 수명 동안 PostgreSQL 인증 서비스를 구성하고 제공한다.

## `open_auth_service`

[소스 선언](../../../../../app/auth/providers/auth_provider.py#L15)

```python
async def open_auth_service(config: Settings) -> AsyncIterator[AuthService | None]:
    ...
```

계정 인증 설정이 있으면 서비스를 열고 앱 종료 시 연결을 해제한다.

**인자**

- config: PostgreSQL 연결 문자열과 JWT 키를 제공하는 앱 설정.

**반환값**

- AsyncIterator[AuthService | None]: 앱 수명의 인증 서비스 또는 인증 미설정 시 None.

## `get_auth_service`

[소스 선언](../../../../../app/auth/providers/auth_provider.py#L38)

```python
def get_auth_service(request: Request) -> AuthService:
    ...
```

FastAPI 앱의 인증 서비스가 준비됐는지 확인한다.

**인자**

- request: 인증 서비스를 보관하는 FastAPI 앱의 요청.

**반환값**

- AuthService: 앱 기동 시 구성한 인증 서비스.

**예외**

- HTTPException: 계정 인증이 설정되지 않았으면 503이 발생한다.
