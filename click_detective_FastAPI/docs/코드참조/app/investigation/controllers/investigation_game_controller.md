# `app/investigation/controllers/investigation_game_controller.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/controllers/investigation_game_controller.py)

수사 생성, 조회와 사용자 행동 API.

## `create_game`

[소스 선언](../../../../../app/investigation/controllers/investigation_game_controller.py#L26)

```python
def create_game(command: NewGame, request: Request):
    ...
```

새 수사를 만들고 게임 토큰을 발급한다. Next.js는 토큰을 HttpOnly 쿠키에 보관한다.

**인자**

- command (NewGame): 사건 ID, 사건 버전과 요청 UUID를 담은 생성 입력.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

- dict: 새 수사 ID, 비밀 게임 토큰과 공개 초기 상태.

## `get_game`

[소스 선언](../../../../../app/investigation/controllers/investigation_game_controller.py#L43)

```python
def get_game(game_id: str, request: Request):
    ...
```

화면용 수사 상태·진행률·자료·타임라인·가능 행동을 집계한다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

- dict: 화면용 정보로 변환한 state 항목.

## `examine`

[소스 선언](../../../../../app/investigation/controllers/investigation_game_controller.py#L57)

```python
async def examine(game_id: str, command: Examine, request: Request):
    ...
```

증거 열람을 한 번 확정한다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- command (Examine): 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

- dict: 요청 ID, 행동별 result와 변경 후 공개 state를 담은 응답.

## `interrogate`

[소스 선언](../../../../../app/investigation/controllers/investigation_game_controller.py#L72)

```python
async def interrogate(game_id: str, command: Interrogate, request: Request):
    ...
```

서버 승인 계획→LangGraph→대화·증언·쟁점 원자적 확정을 수행한다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- command (Interrogate): 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

- dict: 최종 대사 결과와 대화·증언·쟁점이 반영된 공개 상태.

## `infer`

[소스 선언](../../../../../app/investigation/controllers/investigation_game_controller.py#L87)

```python
async def infer(game_id: str, command: Infer, request: Request):
    ...
```

실제로 획득한 정확한 출처 조합으로 추론 문서를 만든다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- command (Infer): 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

- dict: 요청 ID, 행동별 result와 변경 후 공개 state를 담은 응답.

## `advance`

[소스 선언](../../../../../app/investigation/controllers/investigation_game_controller.py#L102)

```python
async def advance(game_id: str, command: Advance, request: Request):
    ...
```

조건을 충족했을 때만 2차 조사와 자동 자료를 공개한다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- command (Advance): 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

- dict: 요청 ID, 행동별 result와 변경 후 공개 state를 담은 응답.

## `notes`

[소스 선언](../../../../../app/investigation/controllers/investigation_game_controller.py#L117)

```python
async def notes(game_id: str, command: Notes, request: Request):
    ...
```

revision을 검사하여 메모를 저장한다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- command (Notes): 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

- dict: 저장 성공 결과와 메모가 반영된 공개 상태.

## `accuse`

[소스 선언](../../../../../app/investigation/controllers/investigation_game_controller.py#L132)

```python
async def accuse(game_id: str, command: Accuse, request: Request):
    ...
```

진행 조건 없이 고발을 받아 선택과 근거를 채점한다. LLM이 정답을 판정하지 않는다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- command (Accuse): 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

- dict: 요청 ID, 행동별 result와 변경 후 공개 state를 담은 응답.
