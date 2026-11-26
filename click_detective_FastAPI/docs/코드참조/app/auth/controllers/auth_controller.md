# `app/auth/controllers/auth_controller.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/controllers/auth_controller.py)

Next.js 서버가 사용하는 인증 HTTP 계약을 제공한다.

## `auth_peer`

[소스 선언](../../../../../app/auth/controllers/auth_controller.py#L15)

```python
def auth_peer(request: Request):
    ...
```

인증 요청 제한에 사용할 신뢰된 연결 상대 주소를 고른다.

**인자**

- request: 서버 중계에서 온 FastAPI 요청.

**반환값**

- str: 연결 상대 주소 또는 알 수 없는 주소의 공통 값.

## `signup`

[소스 선언](../../../../../app/auth/controllers/auth_controller.py#L28)

```python
def signup(command: Credentials, request: Request):
    ...
```

신규 계정을 등록하고 공개 계정 정보를 반환한다.

**인자**

- command: 가입 이메일과 비밀번호.
- request: 인증 서비스에 접근할 FastAPI 요청.

**반환값**

- dict: 인증 토큰을 발급하지 않는 공개 계정 요약.

## `login`

[소스 선언](../../../../../app/auth/controllers/auth_controller.py#L44)

```python
def login(command: Credentials, request: Request):
    ...
```

사용자 자격 증명으로 새 로그인 세션을 연다.

**인자**

- command: 로그인 이메일과 비밀번호.
- request: 인증 서비스에 접근할 FastAPI 요청.

**반환값**

- dict: Next.js 서버가 쿠키로 옮길 토큰과 공개 계정 정보.

## `me`

[소스 선언](../../../../../app/auth/controllers/auth_controller.py#L60)

```python
def me(request: Request):
    ...
```

현재 로그인 계정의 공개 정보를 조회한다.

**인자**

- request: 서버 중계의 접근 토큰이 있는 요청.

**반환값**

- dict: 공개 계정 ID와 정규화된 이메일.

## `refresh`

[소스 선언](../../../../../app/auth/controllers/auth_controller.py#L73)

```python
def refresh(request: Request):
    ...
```

서버 중계의 갱신 토큰을 회전한다.

**인자**

- request: 갱신 토큰 헤더를 읽을 FastAPI 요청.

**반환값**

- dict: 새 토큰 쌍과 각 만료 시각 및 공개 계정 정보.

## `logout`

[소스 선언](../../../../../app/auth/controllers/auth_controller.py#L89)

```python
def logout(request: Request):
    ...
```

현재 로그인 세션을 폐기한다.

**인자**

- request: 접근 또는 갱신 토큰을 읽을 FastAPI 요청.

**반환값**

- dict: 저장소에서 세션 폐기를 확인한 결과.

## `delete_account`

[소스 선언](../../../../../app/auth/controllers/auth_controller.py#L109)

```python
def delete_account(command: DeleteAccount, request: Request):
    ...
```

현재 세션의 계정을 비밀번호 확인 후 탈퇴 대기 상태로 바꾼다.

**인자**

- command: 계정 삭제에 필요한 현재 비밀번호.
- request: 인증 세션과 구성된 수사 저장소에 접근할 요청.

**반환값**

- dict: 모든 세션의 폐기와 작업 등록을 확인한 결과.
