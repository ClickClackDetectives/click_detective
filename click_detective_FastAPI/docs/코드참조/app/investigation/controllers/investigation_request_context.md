# `app/investigation/controllers/investigation_request_context.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/controllers/investigation_request_context.py)

수사 요청의 접근 권한과 상태 변경 경로를 연결한다.

## `investigation_access`

[소스 선언](../../../../../app/investigation/controllers/investigation_request_context.py#L10)

```python
def investigation_access(request: Request):
    ...
```

익명 토큰 또는 검증된 계정 문맥을 선택한다.

**인자**

- request: Next.js가 전달한 수사 접근 헤더를 담은 요청.

**반환값**

- str | AccountAccess: 저장소가 확인할 익명 토큰 또는 계정.

## `game`

[소스 선언](../../../../../app/investigation/controllers/investigation_request_context.py#L26)

```python
def game(request: Request, game_id: str):
    ...
```

게임 토큰과 버전으로 접근 권한을 확인한다.

**인자**

- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
- game_id (str): 조회하거나 변경할 수사의 식별자.

**반환값**

- dict: 접근 토큰과 사건 버전을 확인한 내부 수사 상태.

## `mutate`

[소스 선언](../../../../../app/investigation/controllers/investigation_request_context.py#L40)

```python
async def mutate(request, game_id, command, action):
    ...
```

모든 변경 API가 같은 중복·revision·확정 경로를 사용한다.

**인자**

- request: 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
- game_id: 조회하거나 변경할 수사의 식별자.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- action: 실행할 수사 행동 이름. 예: interrogate, examine.

**반환값**

- dict: 확정된 행동 결과, 요청 ID와 공개 수사 상태.
