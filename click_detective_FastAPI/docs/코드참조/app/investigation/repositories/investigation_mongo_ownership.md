# `app/investigation/repositories/investigation_mongo_ownership.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/repositories/investigation_mongo_ownership.py)

계정의 수사 목록을 조회하고 익명 수사를 계정에 연결한다.

## `summary`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_ownership.py#L14)

```python
def summary(game):
    ...
```

수사 문서에서 소유자 목록에 표시할 필드만 읽는다.

**인자**

- game: 수사 식별자와 최근 상태가 있는 MongoDB 문서.

**반환값**

- dict: 수사 ID, 사건, 버전, 갱신 시각과 진행 요약.

## `cursor_filter`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_ownership.py#L37)

```python
def cursor_filter(cursor):
    ...
```

목록 커서를 MongoDB의 복합 정렬 범위로 변환한다.

**인자**

- cursor: 직전 페이지 마지막 문서의 시각과 UUID를 담은 문자열.

**반환값**

- Q: 다음 페이지의 범위를 표현하는 ODM 조회 조건.

## `list_owned`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_ownership.py#L57)

```python
def list_owned(storage, user_id, cursor, limit):
    ...
```

계정 소유 수사를 가장 최근 갱신 순으로 읽는다.

**인자**

- storage: MongoDB 수사 컬렉션에 접근할 저장소.
- user_id: 인증을 통과한 사용자 UUID.
- cursor: 이전 페이지가 반환한 커서 또는 None.
- limit: 반환할 문서 수로 1~100만 허용한다.

**반환값**

- dict: 현재 페이지의 공개 수사 요약과 다음 커서.

## `claim`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_ownership.py#L94)

```python
def claim(storage, game_id, token, user_id):
    ...
```

익명 수사에 계정 소유권을 부여하고 이전 토큰을 폐기한다.

**인자**

- storage: MongoDB 수사 컬렉션에 접근할 저장소.
- game_id: 연결할 수사 UUID.
- token: 기존 브라우저가 가진 익명 수사 토큰.
- user_id: 연결을 요청한 인증 계정 UUID.

**반환값**

- dict: 연결한 수사의 공개 목록 요약.

## `delete_owned`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_ownership.py#L137)

```python
def delete_owned(storage, user_id):
    ...
```

탈퇴 대기 계정의 모든 수사와 연결된 요청을 삭제한다.

**인자**

- storage: MongoDB 수사 컬렉션에 접근할 저장소.
- user_id: 지울 계정의 UUID. 작업 전에 계정과 세션을 차단한다.

**반환값**

- None: 계정에 남은 수사가 없음을 확인한다.
