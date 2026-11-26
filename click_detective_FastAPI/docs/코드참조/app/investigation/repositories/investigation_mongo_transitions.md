# `app/investigation/repositories/investigation_mongo_transitions.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/repositories/investigation_mongo_transitions.py)

MongoDB에 수사 행동 예약과 완료 결과를 확정한다.

## `reserve`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_transitions.py#L12)

```python
def reserve(storage, game_id, token, command, action, lease_seconds, prepare=None):
    ...
```

수사 행동을 예약하거나 이미 확정한 결과를 읽는다.

**인자**

- storage: MongoDB 수사와 요청 컬렉션을 연결하는 저장소.
- game_id: 수사 UUID.
- token: 익명 접근 토큰 또는 검증된 계정 문맥.
- command: 요청 UUID, 기준 revision, 행동 입력.
- action: 실행할 수사 행동의 이름.
- lease_seconds: 예약 임대 기간(초).
- prepare: 유효한 심문을 준비하는 함수. 제공되면 예약과 함께 질문을 차감한다.

**반환값**

- dict: 실행용 예약 또는 동일 요청의 완료 응답.

## `commit`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_transitions.py#L100)

```python
def commit(storage, game_id, command, reservation, state, result, present):
    ...
```

수사 상태와 요청의 완료 응답을 함께 확정한다.

**인자**

- storage: MongoDB 수사와 요청 컬렉션을 연결하는 저장소.
- game_id: 수사 UUID.
- command: 앞서 예약한 수사 행동 입력.
- reservation: 예약 nonce와 기준 revision 및 소유권 버전.
- state: 행동 처리 뒤의 내부 수사 상태.
- result: 행동 처리 결과.
- present: 내부 상태를 공개 화면 상태로 변환하는 함수.

**반환값**

- dict: 요청 UUID와 행동 결과, 확정한 공개 상태.
