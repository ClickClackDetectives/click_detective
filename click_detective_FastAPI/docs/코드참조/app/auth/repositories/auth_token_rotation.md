# `app/auth/repositories/auth_token_rotation.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/repositories/auth_token_rotation.py)

세션 잠금으로 갱신 토큰 교체와 재사용 감지를 직렬화한다.

## `rotate`

[소스 선언](../../../../../app/auth/repositories/auth_token_rotation.py#L11)

```python
def rotate(repository, previous_hash, next_hash, expected_user):
    ...
```

활성 세션에 새 갱신 토큰을 기록한다.

**인자**

- repository: PostgreSQL 인증 저장소.
- previous_hash: 요청으로 받은 갱신 토큰의 해시.
- next_hash: 새로 발급할 갱신 토큰의 해시.
- expected_user: 갱신 요청을 발생시킨 화면의 계정 ID 또는 None.

**반환값**

- tuple[dict, datetime]: 계정 및 세션 정보와 갱신 시각.

**예외**

- HTTPException: 갱신 토큰이 없거나 세션을 사용할 수 없다.
