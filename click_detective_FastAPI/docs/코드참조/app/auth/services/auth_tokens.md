# `app/auth/services/auth_tokens.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/services/auth_tokens.py)

접근 토큰 JWT와 갱신 토큰의 해시 정책을 제공한다.

## `token_hash`

[소스 선언](../../../../../app/auth/services/auth_tokens.py#L15)

```python
def token_hash(token):
    ...
```

서버에서 발급한 갱신 토큰을 저장용 해시로 바꾼다.

**인자**

- token: 갱신 토큰 원문.

**반환값**

- bytes: 32바이트 SHA-256 해시.

## `issue_pair`

[소스 선언](../../../../../app/auth/services/auth_tokens.py#L27)

```python
def issue_pair(key, user, session_id, now, expires_at, refresh_token):
    ...
```

접근 토큰과 갱신 토큰을 세션의 고정 만료 범위에 맞춰 반환한다.

**인자**

- key: JWT 서명 키.
- user: 계정 ID와 이메일을 담은 공개 요약.
- session_id: 로그인 세션 UUID.
- now: 토큰 발급 UTC 시각.
- expires_at: 최초 로그인에 고정된 세션 종료 UTC 시각.
- refresh_token: 새로 발급한 갱신 토큰 원문.

**반환값**

- dict: 사용자, 두 토큰과 각 만료 시각을 담은 서버용 응답.

## `access_identity`

[소스 선언](../../../../../app/auth/services/auth_tokens.py#L60)

```python
def access_identity(key, token, *, allow_expired=False):
    ...
```

서명과 용도를 검사하고 JWT의 계정 및 세션 ID를 꺼낸다.

**인자**

- key: JWT 검증 키.
- token: 접근 토큰 원문.
- allow_expired: 로그아웃에서만 만료된 서명 토큰의 세션 참조를 허용한다.

**반환값**

- tuple[UUID, UUID]: 인증된 계정 ID와 로그인 세션 ID.

**예외**

- HTTPException: 토큰이 비어 있거나, 유효하지 않거나, 만료되면 발생한다.
