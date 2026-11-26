# `app/auth/dto/auth_contracts.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/dto/auth_contracts.py)

계정 API와 DB 쓰기 계약을 구분한다.

## `Credentials`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L9)

```python
class Credentials(BaseModel):
    ...
```

가입 또는 로그인에 필요한 자격 증명을 검증한다.

**인자**

- email: 이메일 주소.
- password: 비밀번호 원문이며 입력 크기를 제한한다.

**반환값**

- Credentials: 계정 API의 입력 DTO.

## `DeleteAccount`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L25)

```python
class DeleteAccount(BaseModel):
    ...
```

계정 탈퇴 확인에 필요한 현재 비밀번호를 받는다.

**인자**

- password: 본인이 입력한 현재 비밀번호 원문.

**반환값**

- DeleteAccount: 비밀번호 재확인을 위한 탈퇴 요청 DTO.

## `Account`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L39)

```python
class Account(BaseModel):
    ...
```

공개 가능한 계정 필드를 정의한다.

**인자**

- id: 계정 UUID.
- email: 정규화한 이메일.

**반환값**

- Account: 비밀번호와 토큰을 제외한 계정 정보.

## `TokenPair`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L54)

```python
class TokenPair(BaseModel):
    ...
```

서버 중계에서만 사용하는 인증 토큰 응답을 정의한다.

**인자**

- user: 공개 계정 정보.
- access_token: 서명한 접근 토큰 원문.
- refresh_token: 불투명 갱신 토큰 원문.
- access_expires_at: 접근 토큰 만료 UTC 시각.
- refresh_expires_at: 세션과 갱신 토큰의 만료 UTC 시각.

**반환값**

- TokenPair: Next.js 서버에서 쿠키로 옮길 토큰 계약.

## `UserInsert`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L75)

```python
class UserInsert(BaseModel):
    ...
```

사용자 등록에 허용된 PostgreSQL 입력을 묶는다.

**인자**

- id: 생성할 계정 UUID.
- email: 표시용 이메일.
- email_lookup: 중복 확인에 사용할 정규화 키.
- password_hash: Argon2id 해시.
- created_at: 계정 생성 UTC 시각.

**반환값**

- UserInsert: 활성 계정을 등록할 때 사용할 입력.

## `LoginLookup`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L96)

```python
class LoginLookup(BaseModel):
    ...
```

로그인용 계정 조회 키를 보관한다.

**인자**

- email_lookup: 정규화한 이메일의 대소문자 무시 조회 키.

**반환값**

- LoginLookup: 로그인 계정 조회 입력.

## `SessionInsert`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L109)

```python
class SessionInsert(BaseModel):
    ...
```

로그인 세션 및 최초 갱신 토큰의 저장 필드를 묶는다.

**인자**

- id: 로그인 세션 UUID.
- user_id: 비밀번호 검증을 통과한 계정 UUID.
- issued_at: 첫 로그인 UTC 시각.
- expires_at: 로그인 세션의 고정 만료 UTC 시각.
- refresh_hash: 최초 갱신 토큰의 32바이트 SHA-256 해시.

**반환값**

- SessionInsert: 한 트랜잭션으로 등록할 세션 입력.

## `UserInsertBuilder`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L130)

```python
class UserInsertBuilder:
    ...
```

가입 서비스의 처리 결과를 사용자 등록 입력으로 조립한다.

**인자**

- 없음.

**반환값**

- UserInsertBuilder: 호출별 등록 입력을 만드는 빌더.

## `UserInsertBuilder.build`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L141)

```python
def build(email, password_hash, now):
    ...
```

정규화한 이메일과 해시를 등록 입력으로 옮긴다.

**인자**

- email: 정규화한 이메일.
- password_hash: Argon2id 해시.
- now: 계정 생성 UTC 시각.

**반환값**

- UserInsert: 활성 사용자 등록 입력.

## `LoginLookupBuilder`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L161)

```python
class LoginLookupBuilder:
    ...
```

이메일의 로그인 조회 키를 만드는 빌더다.

**인자**

- 없음.

**반환값**

- LoginLookupBuilder: 정규화한 이메일을 조회 모델로 옮기는 빌더.

## `LoginLookupBuilder.build`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L172)

```python
def build(email):
    ...
```

정규화한 이메일에서 대소문자를 무시하는 조회 키를 만든다.

**인자**

- email: 정규화한 이메일.

**반환값**

- LoginLookup: 로그인 계정 조회 입력.

## `SessionInsertBuilder`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L184)

```python
class SessionInsertBuilder:
    ...
```

서버에서 발급한 세션 정보를 저장 입력으로 조립한다.

**인자**

- 없음.

**반환값**

- SessionInsertBuilder: 세션과 최초 갱신 토큰의 저장 모델을 만드는 빌더.

## `SessionInsertBuilder.build`

[소스 선언](../../../../../app/auth/dto/auth_contracts.py#L195)

```python
def build(user_id, issued_at, expires_at, refresh_hash):
    ...
```

첫 로그인 세션을 새 UUID로 구성한다.

**인자**

- user_id: 비밀번호를 검증한 사용자 UUID.
- issued_at: 최초 로그인 UTC 시각.
- expires_at: 최초 로그인에 고정된 종료 UTC 시각.
- refresh_hash: 최초 갱신 토큰의 SHA-256 해시.

**반환값**

- SessionInsert: 트랜잭션 등록 계약.
