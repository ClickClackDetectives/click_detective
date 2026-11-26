# `app/investigation/repositories/investigation_mongo_repository.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/repositories/investigation_mongo_repository.py)

수사 상태와 재시도 기록을 MongoDB 트랜잭션으로 관리한다.

## `MongoRepository`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_repository.py#L28)

```python
class MongoRepository(MongoStorage):
    ...
```

익명·계정 수사에 대한 생성, 조회, 변경과 재시도를 지원한다.

**인자**

- uri: MongoDB replica set의 접속 문자열.
- database: 수사와 요청 기록을 보관할 데이터베이스 이름.

**반환값**

- MongoRepository: GameService에 전달할 MongoDB 저장소.

## `MongoRepository.get`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_repository.py#L39)

```python
def get(self, game_id, token):
    ...
```

현재 권한으로 저장된 수사를 읽는다.

**인자**

- game_id: 조회할 수사의 UUID.
- token: 익명 수사 토큰 또는 서버가 검증한 계정 문맥.

**반환값**

- dict: 수사의 내부 상태.

## `MongoRepository.create`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_repository.py#L52)

```python
def create(self, request, factory, present, owner=None):
    ...
```

새 수사와 같은 요청의 재시도 응답을 함께 저장한다.

**인자**

- request: 사건 ID, 사건 버전과 요청 UUID를 담은 생성 입력.
- factory: 새 수사 UUID로 초기 상태를 생성하는 함수.
- present: 내부 상태를 공개 상태로 바꾸는 함수.
- owner: 새 수사 소유자 UUID 또는 계정 문맥. 익명 시작은 None.

**반환값**

- dict: 수사 ID, 익명 토큰 또는 null, 공개 상태.

## `MongoRepository.reserve`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_repository.py#L129)

```python
def reserve(self, game_id, token, command, action, lease_seconds, prepare=None):
    ...
```

수사 행동을 실행할 예약권을 얻거나 완료 응답을 읽는다.

**인자**

- game_id: 변경할 수사의 UUID.
- token: 익명 수사 토큰 또는 검증된 계정 문맥.
- command: 요청 UUID와 변경 조건 및 입력값.
- action: 실행할 수사 행동의 이름.
- lease_seconds: 예약을 유지할 초 단위 시간.
- prepare: 심문 입력을 검증하는 함수. 제공되면 질문을 함께 차감한다.

**반환값**

- dict: 예약 문맥 또는 저장된 동일 요청의 결과.

## `MongoRepository.commit`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_repository.py#L151)

```python
def commit(self, game_id, command, reservation, state, result, present):
    ...
```

수사 변경과 행동 결과를 같은 트랜잭션에서 확정한다.

**인자**

- game_id: 변경할 수사의 UUID.
- command: 실행권을 예약한 요청.
- reservation: 예약 nonce, 기준 revision, 소유권 버전.
- state: 행동 처리 후 수사 상태.
- result: 공개할 행동 결과.
- present: 내부 상태를 공개 응답으로 바꾸는 함수.

**반환값**

- dict: 요청 ID, 행동 결과와 공개 상태.

## `MongoRepository.abort`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_repository.py#L169)

```python
def abort(self, command, reservation, failure=None):
    ...
```

실패한 예약을 해제하거나 이미 차감한 심문의 오류를 저장한다.

**인자**

- command: 실패한 수사 행동의 입력과 요청 UUID.
- reservation: 실패한 실행의 예약 nonce.
- failure: 예약을 종료하게 한 예외 또는 None.

**반환값**

- None: 해당 nonce의 pending 상태만 갱신한다.

## `MongoRepository.claim`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_repository.py#L199)

```python
def claim(self, game_id, token, user_id):
    ...
```

익명 수사를 인증한 계정 소유로 전환한다.

**인자**

- game_id: 연결할 수사의 UUID.
- token: 익명 수사 토큰.
- user_id: 검증된 계정 UUID.

**반환값**

- dict: 연결된 수사의 공개 요약.

## `MongoRepository.list_owned`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_repository.py#L212)

```python
def list_owned(self, user_id, cursor=None, limit=20):
    ...
```

로그인 계정이 소유한 수사를 최근 갱신 순으로 조회한다.

**인자**

- user_id: 검증된 계정 UUID.
- cursor: 이전 페이지에서 받은 목록 커서 또는 None.
- limit: 한 페이지에 표시할 최대 수사 개수.

**반환값**

- dict: 계정 수사 요약 목록과 다음 페이지 커서.

## `MongoRepository.delete_owned`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_repository.py#L225)

```python
def delete_owned(self, user_id):
    ...
```

탈퇴 대기 계정의 수사와 그 요청 기록을 제거한다.

**인자**

- user_id: 신규 활동과 세션을 먼저 차단한 삭제 대상 계정 UUID.

**반환값**

- None: 계정 수사와 해당 요청 기록의 삭제를 끝낸다.
