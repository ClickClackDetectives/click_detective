# `app/dependencies.py`

[코드 참조 목차](../README.md) · [전체 문서 목차](../../README.md) · [실제 소스](../../../app/dependencies.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 71줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

API 인증과 수사 서비스 접근을 공통으로 제공한다.

## `authenticate`

[소스 선언 위치](../../../app/dependencies.py#L11)

```python
async def authenticate(
    request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)
):
    ...
```

Next.js 서버 전용 API 키를 검사한다. 브라우저에 이 키를 전달하지 않는다.

**파라미터**

- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
- credentials (HTTPAuthorizationCredentials | None): Authorization 헤더에서 읽은 Bearer 인증 정보.

**반환값**

None: 반환값 없음.

## `service`

[소스 선언 위치](../../../app/dependencies.py#L31)

```python
def service(request: Request):
    ...
```

공통 인증을 통과한 API에 게임 서비스를 제공한다.

**파라미터**

- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

GameService: 요청을 받은 앱이 보관하는 수사 처리 서비스.

## `game`

[소스 선언 위치](../../../app/dependencies.py#L43)

```python
def game(request: Request, game_id: str):
    ...
```

게임 토큰과 버전으로 접근 권한을 확인한다.

**파라미터**

- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
- game_id (str): 조회하거나 변경할 수사의 식별자.

**반환값**

dict: 접근 토큰과 사건 버전을 확인한 내부 수사 상태.

## `mutate`

[소스 선언 위치](../../../app/dependencies.py#L57)

```python
async def mutate(request, game_id, command, action):
    ...
```

모든 변경 API가 같은 중복·revision·확정 경로를 사용한다.

**파라미터**

- request: 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
- game_id: 조회하거나 변경할 수사의 식별자.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- action: 실행할 수사 행동 이름. 예: interrogate, examine.

**반환값**

dict: 확정된 행동 결과, 요청 ID와 공개 수사 상태.
