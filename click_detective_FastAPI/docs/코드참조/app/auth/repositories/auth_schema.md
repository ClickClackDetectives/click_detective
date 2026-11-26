# `app/auth/repositories/auth_schema.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/auth/repositories/auth_schema.py)

PostgreSQL 인증 테이블을 SQLAlchemy 모델로 선언한다.

## `AuthBase`

[소스 선언](../../../../../app/auth/repositories/auth_schema.py#L21)

```python
class AuthBase(DeclarativeBase):
    ...
```

인증 테이블의 공통 SQLAlchemy 메타데이터를 제공한다.

**인자**

- 없음.

**반환값**

- AuthBase: PostgreSQL 인증 모델의 선언 기반.

## `User`

[소스 선언](../../../../../app/auth/repositories/auth_schema.py#L32)

```python
class User(AuthBase):
    ...
```

정규화된 이메일을 가진 계정과 비밀번호 해시를 저장한다.

**인자**

- **kwargs: 등록 시 매핑할 계정 열의 값.

**반환값**

- User: 등록된 계정 행을 나타내는 인스턴스.

## `LoginSession`

[소스 선언](../../../../../app/auth/repositories/auth_schema.py#L55)

```python
class LoginSession(AuthBase):
    ...
```

계정에 속한 로그인 세션과 폐기 상태를 저장한다.

**인자**

- **kwargs: 세션의 식별자, 계정과 수명 정보.

**반환값**

- LoginSession: 로그인 세션 행을 나타내는 인스턴스.

## `RefreshToken`

[소스 선언](../../../../../app/auth/repositories/auth_schema.py#L79)

```python
class RefreshToken(AuthBase):
    ...
```

세션의 갱신 토큰 해시와 회전 상태를 저장한다.

**인자**

- **kwargs: 토큰 해시, 세션 참조와 시각 필드.

**반환값**

- RefreshToken: 원문을 제외한 갱신 토큰 행을 나타내는 인스턴스.

## `AttemptBucket`

[소스 선언](../../../../../app/auth/repositories/auth_schema.py#L110)

```python
class AttemptBucket(AuthBase):
    ...
```

이메일 또는 연결 출처별 인증 시도 횟수를 저장한다.

**인자**

- **kwargs: 키 해시, 시간 구간과 시도 횟수.

**반환값**

- AttemptBucket: 분산 인증 요청의 횟수 집계 행을 나타내는 인스턴스.

## `DeletionJob`

[소스 선언](../../../../../app/auth/repositories/auth_schema.py#L131)

```python
class DeletionJob(AuthBase):
    ...
```

계정 삭제 작업의 예약과 처리 상태를 저장한다.

**인자**

- **kwargs: 삭제 작업 및 계정 식별자와 예약 정보.

**반환값**

- DeletionJob: 작업 실행권과 완료 상태를 포함한 인스턴스.
