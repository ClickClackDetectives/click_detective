# `app/investigation/service.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/investigation/service.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 227줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

HTTP와 게임 엔진·모델·원자적 저장을 조정한다. 게임 판정은 전부 Python이 담당한다.

## 함께 읽을 코드

- [app/dialogue/reply_validation.py](../dialogue/reply_validation.md)
- [app/dialogue/schemas.py](../dialogue/schemas.md)

## `GameService`

[소스 선언 위치](../../../../app/investigation/service.py#L17)

```python
class GameService:
    ...
```

수사 생성·조회·변경과 GPU 대사를 연결한다.

**파라미터**

- settings: 모델 실행과 검색에 사용할 설정.
- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- repository: 수사 상태와 요청 예약을 저장하는 객체.
- engine: 게임 진행과 행동의 조건을 판정하는 객체.
- planner: 현재 공개할 사실을 선택하는 객체.
- presenter: 내부 상태를 화면용 정보로 변환하는 객체.
- graph: 대사를 생성·검증하는 그래프. fixture 모드에서는 생략할 수 있다.

**반환값**

GameService: 위 역할을 수행하도록 생성된 객체.

## `GameService.__init__`

[소스 선언 위치](../../../../app/investigation/service.py#L33)

```python
def __init__(
    self, settings, catalog, repository, engine, planner, presenter, graph=None
):
    ...
```

공용 객체를 연결한다. 모델은 서버 시작 시 한 번만 준비한다.

**파라미터**

- settings: 모델 실행과 검색에 사용할 설정.
- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- repository: 수사 상태와 요청 예약을 저장하는 객체.
- engine: 게임 진행과 행동의 조건을 판정하는 객체.
- planner: 현재 공개할 사실을 선택하는 객체.
- presenter: 내부 상태를 화면용 정보로 변환하는 객체.
- graph: 대사를 생성·검증하는 그래프. fixture 모드에서는 생략할 수 있다.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `GameService.read`

[소스 선언 위치](../../../../app/investigation/service.py#L61)

```python
def read(self, game_id, token):
    ...
```

소유권과 사건 버전을 검사해 저장 상태를 복원한다.

**파라미터**

- game_id: 조회하거나 변경할 수사의 식별자.
- token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.

**반환값**

dict: 소유권과 사건 버전을 확인한 수사 상태.

## `GameService.create`

[소스 선언 위치](../../../../app/investigation/service.py#L76)

```python
def create(self, command):
    ...
```

실행 가능한 사건·버전을 확인하고 생성 중복을 처리한다.

**파라미터**

- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

**반환값**

dict: 수사 ID, 접근 토큰과 공개 초기 상태 또는 저장된 동일 요청 결과.

## `GameService.dialogue_request`

[소스 선언 위치](../../../../app/investigation/service.py#L92)

```python
def dialogue_request(self, state, command, plan):
    ...
```

저장 상태와 승인 계획에서 모델 DTO를 만든다. 외부 임의 승인 사실을 받지 않는다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- plan: 게임 규칙이 승인한 사실과 기록 예정 정보를 담은 계획.

**반환값**

CharacterReplyRequest: 승인 사실, 필수 ID, 인물과 최근 대화를 담은 요청.

## `GameService.reply`

[소스 선언 위치](../../../../app/investigation/service.py#L134)

```python
async def reply(self, request):
    ...
```

쟁점 유무와 무관하게 대사를 준비하고 모델 실패는 승인 원문으로 복구한다.

생성 대사를 검증 없이 통과시키지 않는다. 복구 대사는 서버가 승인한 사실만
사용하므로 원래 쟁점·증언 계획을 안전하게 확정할 수 있다. strict 설정에서는
오류를 그대로 전달하여 모델 품질 검사에 사용할 수 있다.

**파라미터**

- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

**반환값**

CharacterReplyResponse: 생성·검증을 통과했거나 승인 원문으로 복구한 응답.

## `GameService.change`

[소스 선언 위치](../../../../app/investigation/service.py#L185)

```python
async def change(self, game_id, token, command, action):
    ...
```

유효한 심문을 예약할 때 질문을 차감하고 최종 대화는 별도로 확정한다.

**파라미터**

- game_id: 조회하거나 변경할 수사의 식별자.
- token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- action: 실행할 수사 행동 이름. 예: interrogate, examine.

**반환값**

dict: 확정한 행동 결과와 최신 공개 상태 또는 저장된 동일 요청 응답.

수사 읽기와 변경은 저장소에 익명 토큰 또는 검증된 계정 문맥을 전달한다. 모델 입력 조립은 [dialogue_request.py](../../../../app/investigation/dialogue_request.py)를 호출한다.
