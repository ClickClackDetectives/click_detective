# `app/investigation/controllers/investigation_account_controller.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/controllers/investigation_account_controller.py)

계정이 소유한 수사 목록과 익명 수사 연결을 제공한다.

## `Claim`

[소스 선언](../../../../../app/investigation/controllers/investigation_account_controller.py#L16)

```python
class Claim(DTO):
    ...
```

현재 브라우저가 계정에 연결할 수사의 입력을 검증한다.

**인자**

- game_id: 연결할 익명 수사의 UUID.

**반환값**

- Claim: 형식을 검사한 연결 요청.

## `list_investigations`

[소스 선언](../../../../../app/investigation/controllers/investigation_account_controller.py#L30)

```python
def list_investigations(request: Request, cursor: Annotated[str | None, Query(max_length=250)]=None, limit: Annotated[int, Query(ge=1, le=50)]=20):
    ...
```

세션이 활성화된 사용자의 수사를 최근 갱신 순으로 조회한다.

**인자**

- request: 계정 접근 헤더와 서비스가 연결된 요청.
- cursor: 직전 페이지가 반환한 위치 또는 첫 페이지에서 None.
- limit: 한 페이지에 반환할 수사 수.

**반환값**

- dict: 공개 수사 요약 목록과 다음 페이지 커서.

## `claim_investigation`

[소스 선언](../../../../../app/investigation/controllers/investigation_account_controller.py#L50)

```python
def claim_investigation(command: Claim, request: Request):
    ...
```

익명 토큰으로 수사를 확인해 현재 계정에 연결한다.

**인자**

- command: 연결할 익명 수사 ID가 포함된 요청.
- request: 세션과 익명 토큰이 포함된 요청.

**반환값**

- dict: 계정으로 연결한 수사의 공개 요약.
