# `app/dialogue/providers/dialogue_provider.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/dialogue/providers/dialogue_provider.py)

대화 그래프와 앱 수명 동안 사용하는 검색 인덱스를 조립한다.

## `open_reply_service`

[소스 선언](../../../../../app/dialogue/providers/dialogue_provider.py#L16)

```python
async def open_reply_service(config: Settings, catalog: Catalog) -> AsyncIterator[ReplyService]:
    ...
```

설정에 따라 검색기와 로컬 모델을 준비하고 검색 인덱스를 정리한다.

**인자**

- config: 모델 실행 모드와 검색 설정.
- catalog: 검색기에서 공개할 수 있는 사건 데이터를 조회하는 저장소.

**반환값**

- AsyncIterator[ReplyService]: 앱 실행 중 사용하는 대화 서비스.

## `get_reply_service`

[소스 선언](../../../../../app/dialogue/providers/dialogue_provider.py#L68)

```python
def get_reply_service(request: Request) -> ReplyService:
    ...
```

앱 기동 시 구성한 대화 서비스를 제공한다.

**인자**

- request: 실행 중인 FastAPI 앱에 접근하는 요청.

**반환값**

- ReplyService: 현재 앱의 대화 처리 서비스.
