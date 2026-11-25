# `app/bootstrap.py`

[코드 참조 목차](../README.md) · [전체 문서 목차](../../README.md) · [실제 소스](../../../app/bootstrap.py)

> 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

서버가 시작될 때 사건, 수사 서비스와 대화 모델을 준비한다. MongoDB ODM 저장소를 열고, 계정 기능을 사용하면 PostgreSQL ORM 엔진을 준비한다. 종료 시 두 저장소의 연결을 정리한다.

## 함께 읽을 코드

- [app/cases/catalog.py](cases/catalog.md)
- [app/config.py](config.md)
- [app/dialogue/preprocess_agent/planning.py](dialogue/preprocess_agent/planning.md)
- [app/investigation/rules/engine.py](investigation/rules/engine.md)
- [app/investigation/views/presentation.py](investigation/views/presentation.md)
- [app/investigation/service.py](investigation/service.md)

## `lifespan`

[소스 선언 위치](../../../app/bootstrap.py#L16)

```python
async def lifespan(app):
    ...
```

정적 데이터와 모델은 한 번 로딩한다. fixture 모드에서만 GPU를 생략한다.

**파라미터**

- app: 설정과 서비스를 보관할 FastAPI 애플리케이션.

**반환값**

AsyncIterator[None]: 앱의 시작 준비를 끝낸 뒤 실행을 서버에 넘기는 비동기 반복자.
