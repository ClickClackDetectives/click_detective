# `app/auth/controllers/auth_request_context.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/controllers/auth_request_context.py)

서버 중계 요청의 계정 인증 문맥을 읽는다.

## `current_user`

[소스 선언](../../../../../app/auth/controllers/auth_request_context.py#L9)

```python
def current_user(request: Request):
    ...
```

서버 중계가 제공한 접근 토큰과 기대 계정을 검증한다.

**인자**

- request: 서버 중계의 인증 헤더가 들어있는 요청.

**반환값**

- dict: 인증된 계정 ID와 이메일.
