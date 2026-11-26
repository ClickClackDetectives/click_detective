# `scripts/live_dialogue/transport.py`

[코드 참조 목차](../../README.md) · [스크립트 목차](../README.md) · [실제 소스](../../../../scripts/live_dialogue/transport.py)

HTTP 왕복 기록과 비밀값 마스킹을 담당한다.

## `LiveTransport`

[소스 선언](../../../../scripts/live_dialogue/transport.py#L10)

```python
class LiveTransport:
    ...
```

실서버 HTTP 요청과 응답을 기록하고 비밀값을 가린다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.
- api_key: 서버 인증에 사용할 비밀 API 키.

**반환값**

- LiveTransport: 위 역할을 수행하도록 생성된 객체.

## `LiveTransport.__init__`

[소스 선언](../../../../scripts/live_dialogue/transport.py#L21)

```python
def __init__(self, client, api_key):
    ...
```

사용할 의존성과 초기 상태를 준비한다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.
- api_key: 서버 인증에 사용할 비밀 API 키.

**반환값**

- None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.

## `LiveTransport.redact`

[소스 선언](../../../../scripts/live_dialogue/transport.py#L35)

```python
def redact(self, value):
    ...
```

헤더·토큰 필드와 문자열에 포함된 실제 비밀값까지 가린다.

**인자**

- value: 검사·변환하거나 비밀값을 가릴 입력 값.

**반환값**

- 입력과 같은 구조의 값: 인증 정보와 알려진 비밀값을 가린 결과.

## `LiveTransport.exchange`

[소스 선언](../../../../scripts/live_dialogue/transport.py#L60)

```python
def exchange(self, rows, method, path, body=None, token=None, purpose='preparation'):
    ...
```

assertion 전에 왕복을 기록한다. 타임아웃도 요청 UUID·본문을 남긴다.

**인자**

- rows: HTTP 왕복 기록을 추가할 목록.
- method: HTTP 요청 메서드. 예: GET, POST.
- path: 저장 파일 경로나 HTTP 요청 경로.
- body: 전송하거나 비교할 JSON 요청 본문.
- token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.
- purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

**반환값**

- dict: 성공한 HTTP 응답의 JSON 객체. 왕복 기록은 rows에도 추가한다.
