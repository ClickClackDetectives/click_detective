# `app/auth/services/auth_service.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/services/auth_service.py)

가입과 로그인 및 토큰 수명을 관리한다.

## `public_user`

[소스 선언](../../../../../app/auth/services/auth_service.py#L25)

```python
def public_user(row):
    ...
```

DB에서 읽은 내부 행을 공개 계정 정보로 제한한다.

**인자**

- row: 문자열로 변환할 계정 ID와 이메일을 포함한 저장 행.

**반환값**

- dict: 공개 계정 ID와 이메일.

## `login_failed`

[소스 선언](../../../../../app/auth/services/auth_service.py#L37)

```python
def login_failed():
    ...
```

가입 여부와 비밀번호 오류를 공통 메시지로 나타낸다.

**인자**

- 없음.

**반환값**

- HTTPException: 잘못된 로그인 요청의 오류.

## `AuthService`

[소스 선언](../../../../../app/auth/services/auth_service.py#L49)

```python
class AuthService:
    ...
```

계정과 세션 유스케이스를 제공하고 저장소 수명을 관리한다.

**인자**

- postgres_dsn: 인증 PostgreSQL 연결 문자열.
- jwt_secret: 32바이트 이상인 HS256 서명 키.

**반환값**

- AuthService: FastAPI 앱이 공유하는 계정 인증 서비스.

## `AuthService.__init__`

[소스 선언](../../../../../app/auth/services/auth_service.py#L60)

```python
def __init__(self, postgres_dsn, jwt_secret):
    ...
```

인증 저장소와 비밀번호 해시 정책을 준비한다.

**인자**

- postgres_dsn: 인증 PostgreSQL 연결 문자열.
- jwt_secret: 32바이트 이상인 HS256 서명 키.

**반환값**

- None: 반환값 없음.

## `AuthService.close`

[소스 선언](../../../../../app/auth/services/auth_service.py#L77)

```python
def close(self):
    ...
```

인증 PostgreSQL 연결 풀을 닫는다.

**인자**

- 없음.

**반환값**

- None: 반환값 없음.

## `AuthService.throttle`

[소스 선언](../../../../../app/auth/services/auth_service.py#L88)

```python
def throttle(self, action, email, peer):
    ...
```

가입 또는 로그인에서 이메일과 연결 상대의 사용량을 제한한다.

**인자**

- action: 가입 또는 로그인 작업 이름.
- email: 브라우저가 입력한 계정 주소.
- peer: 로그인 요청을 전달한 연결 상대 주소.

**반환값**

- None: 할당량 안에서 요청을 진행한다.

## `AuthService.signup`

[소스 선언](../../../../../app/auth/services/auth_service.py#L108)

```python
def signup(self, email, password):
    ...
```

이메일과 비밀번호 정책을 검사하고 새 활성 계정을 등록한다.

**인자**

- email: 대소문자 무시 중복 확인을 적용할 주소.
- password: 영문, 숫자, 특수문자를 각각 포함한 8~16자 비밀번호 원문.

**반환값**

- dict: 공개 계정 ID와 이메일.

## `AuthService.login`

[소스 선언](../../../../../app/auth/services/auth_service.py#L141)

```python
def login(self, email, password):
    ...
```

등록 여부를 노출하지 않고 자격 증명을 확인하여 새 세션을 연다.

**인자**

- email: 등록한 이메일 주소.
- password: 확인할 비밀번호 원문.

**반환값**

- dict: 공개 계정, 접근 및 갱신 토큰, 각각의 만료 시각.

## `AuthService.me`

[소스 선언](../../../../../app/auth/services/auth_service.py#L174)

```python
def me(self, access_token):
    ...
```

접근 JWT와 세션의 현재 유효성을 확인한다.

**인자**

- access_token: Next.js 서버가 보낸 접근 토큰 원문.

**반환값**

- dict: 접근 토큰의 공개 계정 ID와 이메일.

## `AuthService.refresh`

[소스 선언](../../../../../app/auth/services/auth_service.py#L189)

```python
def refresh(self, refresh_token, *, expected_user=None):
    ...
```

이전 갱신 토큰을 사용 처리하고 세션 만료 내의 토큰 쌍을 재발급한다.

**인자**

- refresh_token: 아직 사용되지 않은 현재 갱신 토큰 원문.
- expected_user: 갱신 요청을 발생시킨 화면의 계정 ID 또는 None.

**반환값**

- dict: 교체된 두 토큰과 공개 계정 및 만료 시각.

## `AuthService.delete`

[소스 선언](../../../../../app/auth/services/auth_service.py#L217)

```python
def delete(self, user_id, password):
    ...
```

현재 비밀번호를 확인하고 계정 데이터 삭제를 예약한다.

**인자**

- user_id: 요청에서 인증한 사용자 UUID.
- password: 탈퇴 확인용 현재 비밀번호 원문.

**반환값**

- None: 계정 상태 변경, 모든 세션 폐기 및 작업 등록이 완료된다.

## `AuthService.logout`

[소스 선언](../../../../../app/auth/services/auth_service.py#L229)

```python
def logout(self, refresh_token, access_token, *, expected_user=None):
    ...
```

저장소가 응답한 뒤 현재 로그인 세션의 폐기를 완료한다.

**인자**

- refresh_token: 만료된 접근 토큰을 대신해 세션을 식별하는 갱신 토큰 원문.
- access_token: 갱신 쿠키가 없어도 세션을 식별할 수 있는 서명 토큰 원문.
- expected_user: 로그아웃 요청을 발생시킨 화면의 계정 ID 또는 None.

**반환값**

- None: 폐기할 세션이 없거나 이미 폐기된 경우도 정상 완료한다.
