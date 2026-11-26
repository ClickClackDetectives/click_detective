# `app/runtime/runtime_lifespan.py`

[코드 참조 목차](../../README.md) · [도메인 목차](README.md) · [실제 소스](../../../../app/runtime/runtime_lifespan.py)

서버가 시작될 때 사건, 수사 서비스와 대화 모델을 준비한다.

## `lifespan`

[소스 선언](../../../../app/runtime/runtime_lifespan.py#L17)

```python
async def lifespan(app, *, settings: Settings | None=None):
    ...
```

도메인 provider에서 앱의 서비스를 준비하고 종료 시 자원을 해제한다.

**인자**

- app: 설정과 서비스를 보관할 FastAPI 애플리케이션.
- settings: 명시적으로 주입한 설정. None이면 앱 시작 시 환경 설정을 읽는다.

**반환값**

- AsyncIterator[None]: 앱의 시작 준비를 끝낸 뒤 실행을 서버에 넘기는 비동기 반복자.
