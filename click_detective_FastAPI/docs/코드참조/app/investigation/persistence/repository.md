# `app/investigation/persistence/repository.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/investigation/persistence/repository.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 237줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

SQLite 수사 저장·권한·요청 예약·원자적 확정. 모델 실행 동안 DB 잠금을 잡지 않는다.

## 함께 읽을 코드

- [app/investigation/persistence/storage.py](storage.md)

## `Repository`

[소스 선언 위치](../../../../../app/investigation/persistence/repository.py#L17)

```python
class Repository:
    ...
```

전체 수사 상태와 완료 요청을 저장한다. 모델 프롬프트·원본 검증 출력은 저장하지 않는다.

**파라미터**

- path (Path): 수사 상태와 요청 기록을 저장할 SQLite 파일 경로.

**반환값**

Repository: 위 역할을 수행하도록 생성된 객체.

## `Repository.__init__`

[소스 선언 위치](../../../../../app/investigation/persistence/repository.py#L27)

```python
def __init__(self, path: Path):
    ...
```

게임 DB를 준비한다. 기존 기록은 삭제하지 않는다.

**파라미터**

- path (Path): 수사 상태와 요청 기록을 저장할 SQLite 파일 경로.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `Repository.transaction`

[소스 선언 위치](../../../../../app/investigation/persistence/repository.py#L47)

```python
def transaction(self):
    ...
```

짧은 쓰기 트랜잭션을 제공한다. 실패 시 롤백하고 연결을 항상 닫는다.

**파라미터**

- 없음.

**반환값**

ContextManager: SQLite 연결을 제공하고 성공 시 commit, 실패 시 rollback하는 문맥 관리자.

## `Repository._game`

[소스 선언 위치](../../../../../app/investigation/persistence/repository.py#L58)

```python
def _game(self, db, game_id, token):
    ...
```

수사별 비밀 토큰을 검사한다. 다른 수사의 존재도 응답으로 노출하지 않는다.

**파라미터**

- db: 현재 트랜잭션의 SQLite 연결.
- game_id: 조회하거나 변경할 수사의 식별자.
- token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.

**반환값**

dict: 소유권을 확인한 저장 상태. 권한이 없으면 HTTPException을 낸다.

## `Repository.get`

[소스 선언 위치](../../../../../app/investigation/persistence/repository.py#L75)

```python
def get(self, game_id, token):
    ...
```

저장된 수사를 복원한다. 조회만으로 게임 상태를 바꾸지 않는다.

**파라미터**

- game_id: 조회하거나 변경할 수사의 식별자.
- token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.

**반환값**

dict: 접근 권한을 확인한 수사의 저장 상태.

## `Repository.create`

[소스 선언 위치](../../../../../app/investigation/persistence/repository.py#L88)

```python
def create(self, request, factory, present):
    ...
```

초기 수사와 재전송 응답을 같은 트랜잭션에서 저장한다.

**파라미터**

- request: 생성할 사건 ID와 버전, 요청 UUID를 담은 새 수사 입력.
- factory: 게임 ID를 받아 초기 상태를 만드는 함수.
- present: 내부 상태를 공개 응답으로 변환하는 함수.

**반환값**

dict: 수사 ID, 접근 토큰과 공개 초기 상태 또는 저장된 동일 요청 결과.

## `Repository.reserve`

[소스 선언 위치](../../../../../app/investigation/persistence/repository.py#L130)

```python
def reserve(self, game_id, token, command, action, lease_seconds):
    ...
```

실행권을 예약하고 상태 사본을 반환한다. 완료 재전송은 revision 검사보다 먼저 처리한다.

**파라미터**

- game_id: 조회하거나 변경할 수사의 식별자.
- token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- action: 실행할 수사 행동 이름. 예: interrogate, examine.
- lease_seconds: 작업 예약을 유효하게 유지할 초 단위 시간.

**반환값**

dict: 예약 식별값·상태 사본·버전 또는 동일 요청의 캐시된 응답.

## `Repository.commit`

[소스 선언 위치](../../../../../app/investigation/persistence/repository.py#L179)

```python
def commit(self, game_id, command, reservation, state, result, present):
    ...
```

예약 소유권과 최신 revision을 다시 확인하고 결과·상태를 한 번 확정한다.

**파라미터**

- game_id: 조회하거나 변경할 수사의 식별자.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- reservation: 작업의 상태 사본, 예약 식별값과 기준 버전.
- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- result: 행동 처리 결과로 공개할 정보.
- present: 내부 상태를 공개 응답으로 변환하는 함수.

**반환값**

dict: 요청 ID, 행동 결과와 저장된 공개 상태.

## `Repository.abort`

[소스 선언 위치](../../../../../app/investigation/persistence/repository.py#L223)

```python
def abort(self, command, reservation):
    ...
```

실패한 자신의 예약만 재시도 가능 상태로 바꾼다. 새 예약을 지우지 않는다.

**파라미터**

- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- reservation: 작업의 상태 사본, 예약 식별값과 기준 버전.

**반환값**

None: 반환값 없음.
