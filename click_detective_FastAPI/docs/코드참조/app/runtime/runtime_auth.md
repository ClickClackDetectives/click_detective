# `app/runtime/runtime_auth.py`

[코드 참조 목차](../../README.md) · [도메인 목차](README.md) · [실제 소스](../../../../app/runtime/runtime_auth.py)

서버 간 API 인증을 공통으로 제공한다.

## `authenticate`

[소스 선언](../../../../app/runtime/runtime_auth.py#L11)

```python
async def authenticate(request: Request, credentials: HTTPAuthorizationCredentials | None=Depends(bearer)):
    ...
```

Next.js 서버 전용 API 키를 검사한다. 브라우저에 이 키를 전달하지 않는다.

**인자**

- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
- credentials (HTTPAuthorizationCredentials | None): Authorization 헤더에서 읽은 Bearer 인증 정보.

**반환값**

- None: 반환값 없음.
