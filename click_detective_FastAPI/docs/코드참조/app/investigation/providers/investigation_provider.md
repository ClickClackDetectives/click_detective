# `app/investigation/providers/investigation_provider.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/providers/investigation_provider.py)

수사 저장소와 게임 서비스를 앱 시작 시 조립한다.

## `open_investigation_repository`

[소스 선언](../../../../../app/investigation/providers/investigation_provider.py#L24)

```python
async def open_investigation_repository(config: Settings) -> AsyncIterator[MongoRepository]:
    ...
```

현재 앱의 MongoDB 수사 저장소를 열고 종료할 때 연결을 닫는다.

**인자**

- config: MongoDB 연결 문자열과 데이터베이스 이름을 담은 설정.

**반환값**

- AsyncIterator[MongoRepository]: 앱 수명 동안 사용할 수사 저장소.

**예외**

- RuntimeError: MongoDB 연결 문자열이 설정되지 않은 경우.

## `build_game_service`

[소스 선언](../../../../../app/investigation/providers/investigation_provider.py#L49)

```python
def build_game_service(config: Settings, catalog_service: CatalogService, repository: MongoRepository, reply_service: ReplyService) -> GameService:
    ...
```

규칙 엔진, 승인 계획, 화면 조립과 대화 서비스를 수사 흐름에 연결한다.

**인자**

- config: 수사와 대화에 적용할 앱 설정.
- catalog_service: 앱 시작 시 준비한 사건 카탈로그 서비스.
- repository: 수사 상태를 영속화할 MongoDB 저장소.
- reply_service: 승인된 문맥에서 대사를 생성할 대화 서비스.

**반환값**

- GameService: 생성·조회·수사 행동을 처리하는 서비스.

## `get_game_service`

[소스 선언](../../../../../app/investigation/providers/investigation_provider.py#L80)

```python
def get_game_service(request: Request) -> GameService:
    ...
```

앱 기동 시 구성한 수사 서비스를 제공한다.

**인자**

- request: 실행 중인 FastAPI 앱에 접근하는 요청.

**반환값**

- GameService: 현재 앱의 수사 처리 서비스.
