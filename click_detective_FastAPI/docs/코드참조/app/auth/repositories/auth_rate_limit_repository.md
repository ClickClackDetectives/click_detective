# `app/auth/repositories/auth_rate_limit_repository.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/repositories/auth_rate_limit_repository.py)

계정과 요청 출처별 인증 시도를 PostgreSQL에서 제한한다.

## `reserve_attempt`

[소스 선언](../../../../../app/auth/repositories/auth_rate_limit_repository.py#L16)

```python
def reserve_attempt(db, bucket_key, window_number, limit):
    ...
```

정해진 구간에서 인증 시도 횟수를 한 번 증가시킨다.

**인자**

- db: 현재 인증 ORM 세션.
- bucket_key: 이메일 또는 연결 주소의 HMAC.
- window_number: 현재 시간 구간 번호.
- limit: 현재 구간에서 허용하는 최대 시도 수.

**반환값**

- bool: 시도를 기록했으면 참, 상한에 도달했으면 거짓.

## `check_attempt`

[소스 선언](../../../../../app/auth/repositories/auth_rate_limit_repository.py#L39)

```python
def check_attempt(repository, key, action, email, peer):
    ...
```

고비용 비밀번호 처리 전에 다중 인스턴스의 사용량을 합산한다.

**인자**

- repository: PostgreSQL 인증 저장소.
- key: 이메일과 출처를 가리는 HMAC 비밀 키.
- action: signup 또는 login.
- email: 정규화한 계정 조회 키.
- peer: 인증 요청이 들어온 연결 상대 주소.

**반환값**

- None: 허용된 요청만 진행하며 제한 초과 시 HTTP 오류를 낸다.
