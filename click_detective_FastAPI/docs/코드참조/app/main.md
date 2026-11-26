# `app/main.py`

[코드 참조 목차](../README.md) · [실제 소스](../../../app/main.py)

FastAPI 애플리케이션을 만들고 도메인별 API를 연결한다.

## `create_app`

[소스 선언](../../../app/main.py#L32)

```python
def create_app(settings: Settings | None=None):
    ...
```

앱을 구성한다. 실제 데이터·DB·모델 준비는 lifespan에서 수행한다.

**인자**

- settings (Settings | None): 모델 실행과 검색에 사용할 설정.

**반환값**

- FastAPI: 도메인별 API와 시작 절차를 연결한 애플리케이션.

## `create_app.invalid_input`

[소스 선언](../../../app/main.py#L49)

```python
async def invalid_input(_request, error):
    ...
```

원문·토큰을 오류 응답에 복사하지 않고 위치·오류 종류만 반환한다.

**인자**

- _request: FastAPI가 오류 처리기에 전달하는 HTTP 요청.
- error: 현재 처리할 예외 또는 입력 검증 오류.

**반환값**

- JSONResponse: 민감한 원문을 제외하고 오류 위치·종류만 담은 HTTP 422 응답.

## `create_app.investigation_store_unavailable`

[소스 선언](../../../app/main.py#L70)

```python
async def investigation_store_unavailable(request, error):
    ...
```

수사 저장 오류를 재시도 가능한 공개 응답으로 변환한다.

**인자**

- request: 저장소 오류가 발생한 요청.
- error: 접속 정보가 포함될 수 있는 저장소 예외.

**반환값**

- JSONResponse: 기존 요청 UUID를 유지해 재시도할 수 있는 503 응답.

## `create_app.no_store`

[소스 선언](../../../app/main.py#L91)

```python
async def no_store(request, call_next):
    ...
```

수사별 데이터가 브라우저나 프록시의 공용 캐시에 남지 않게 한다.

**인자**

- request: 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
- call_next: 다음 HTTP 처리 단계로 요청을 전달하는 함수.

**반환값**

- Response: Cache-Control: no-store 헤더를 추가한 HTTP 응답.

## `create_app.health`

[소스 선언](../../../app/main.py#L106)

```python
async def health():
    ...
```

서버 시작 완료를 확인한다. 모델 품질 시험을 실행하지 않는다.

**인자**

- 없음.

**반환값**

- dict[str, str]: 서버 준비 상태를 나타내는 status=ok 정보.
