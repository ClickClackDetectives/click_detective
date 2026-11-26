# `app/investigation/services/investigation_game_service.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/services/investigation_game_service.py)

HTTP와 게임 엔진·모델·원자적 저장을 조정한다. 게임 판정은 전부 Python이 담당한다.

## `GameService`

[소스 선언](../../../../../app/investigation/services/investigation_game_service.py#L19)

```python
class GameService:
    ...
```

수사 생성·조회·변경과 GPU 대사를 연결한다.

**인자**

- settings: 모델 실행과 검색에 사용할 설정.
- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- repository: 수사 상태와 요청 예약을 저장하는 객체.
- engine: 게임 진행과 행동의 조건을 판정하는 객체.
- planner: 현재 공개할 사실을 선택하는 객체.
- presenter: 내부 상태를 화면용 정보로 변환하는 객체.
- reply_service: 승인 문맥으로 대사를 생성하고 검증하는 서비스.
- search_free: 그래프에서 자유 질문의 진술을 검색할 수 있는지 여부.

**반환값**

- GameService: 위 역할을 수행하도록 생성된 객체.

## `GameService.__init__`

[소스 선언](../../../../../app/investigation/services/investigation_game_service.py#L36)

```python
def __init__(self, settings, catalog, repository, engine, planner, presenter, reply_service: ReplyService, *, search_free=False):
    ...
```

공용 객체를 연결한다. 모델은 서버 시작 시 한 번만 준비한다.

**인자**

- settings: 모델 실행과 검색에 사용할 설정.
- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- repository: 수사 상태와 요청 예약을 저장하는 객체.
- engine: 게임 진행과 행동의 조건을 판정하는 객체.
- planner: 현재 공개할 사실을 선택하는 객체.
- presenter: 내부 상태를 화면용 정보로 변환하는 객체.
- reply_service: 승인 문맥으로 대사를 생성하고 검증하는 서비스.
- search_free: 그래프에서 자유 질문의 진술을 검색할 수 있는지 여부.

**반환값**

- None: 필요한 설정과 초기값을 저장한다.

## `GameService.read`

[소스 선언](../../../../../app/investigation/services/investigation_game_service.py#L72)

```python
def read(self, game_id, token):
    ...
```

소유권과 사건 버전을 검사해 저장 상태를 복원한다.

**인자**

- game_id: 조회하거나 변경할 수사의 식별자.
- token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.

**반환값**

- dict: 소유권과 사건 버전을 확인한 수사 상태.

## `GameService.create`

[소스 선언](../../../../../app/investigation/services/investigation_game_service.py#L87)

```python
def create(self, command, owner=None):
    ...
```

사건 버전을 확인하고 익명 또는 계정 수사를 한 번만 생성한다.

**인자**

- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- owner: 계정 접근 주체. 익명 수사에서는 None.

**반환값**

- dict: 수사 ID, 접근 토큰과 공개 초기 상태 또는 저장된 동일 요청 결과.

## `GameService.dialogue_request`

[소스 선언](../../../../../app/investigation/services/investigation_game_service.py#L105)

```python
def dialogue_request(self, state, command, plan):
    ...
```

저장 상태와 승인 계획에서 모델 DTO를 만든다. 외부 임의 승인 사실을 받지 않는다.

**인자**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- plan: 게임 규칙이 승인한 사실과 기록 예정 정보를 담은 계획.

**반환값**

- CharacterReplyRequest: 승인 사실, 필수 ID, 인물과 최근 대화를 담은 요청.

## `GameService.change`

[소스 선언](../../../../../app/investigation/services/investigation_game_service.py#L120)

```python
async def change(self, game_id, token, command, action):
    ...
```

유효한 심문을 예약할 때 질문을 차감하고 최종 대화는 별도로 확정한다.

**인자**

- game_id: 조회하거나 변경할 수사의 식별자.
- token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- action: 실행할 수사 행동 이름. 예: interrogate, examine.

**반환값**

- dict: 확정한 행동 결과와 최신 공개 상태 또는 저장된 동일 요청 응답.
