# `scripts/live_dialogue/tester.py`

[코드 참조 목차](../../README.md) · [스크립트 목차](../README.md) · [실제 소스](../../../../scripts/live_dialogue/tester.py)

실서버 대화 검사 사례와 보고서 생성을 조정한다.

## `LiveLlmTester`

[소스 선언](../../../../scripts/live_dialogue/tester.py#L14)

```python
class LiveLlmTester:
    ...
```

실서버 대화 검사 사례와 보고서를 관리한다.

**인자**

- client (httpx.Client): HTTP 요청을 실행하는 클라이언트.
- api_key (str): 서버 인증에 사용할 비밀 API 키.
- data_dir (Path): 사건 JSON 데이터가 있는 디렉터리.
- expected_model_version (str | None): 응답에서 기대하는 정확한 모델 버전. None이면 일치 검사를 생략한다.

**반환값**

- LiveLlmTester: 위 역할을 수행하도록 생성된 객체.

## `LiveLlmTester.__init__`

[소스 선언](../../../../scripts/live_dialogue/tester.py#L27)

```python
def __init__(self, client: httpx.Client, api_key: str, data_dir: Path, expected_model_version: str | None=None):
    ...
```

HTTP 클라이언트를 외부에서 받아 단위 검사에서는 네트워크 없이 검사할 수 있다.

**인자**

- client (httpx.Client): HTTP 요청을 실행하는 클라이언트.
- api_key (str): 서버 인증에 사용할 비밀 API 키.
- data_dir (Path): 사건 JSON 데이터가 있는 디렉터리.
- expected_model_version (str | None): 응답에서 기대하는 정확한 모델 버전. None이면 일치 검사를 생략한다.

**반환값**

- None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.

## `LiveLlmTester.redact`

[소스 선언](../../../../scripts/live_dialogue/tester.py#L65)

```python
def redact(self, value):
    ...
```

보고서에 포함된 비밀값을 가린다.

**인자**

- value: 검사·변환하거나 비밀값을 가릴 입력 값.

**반환값**

- 입력과 같은 구조의 값: 인증 정보와 알려진 비밀값을 가린 결과.

## `LiveLlmTester.run_agents`

[소스 선언](../../../../scripts/live_dialogue/tester.py#L76)

```python
def run_agents(self, inputs, *, progress=False):
    ...
```

게임 API 호출 없이 각 입력을 순서대로 검사한다.

**인자**

- inputs: 요청 UUID를 포함한 대화 입력 하나 또는 입력 목록.
- progress: 각 요청을 보내기 전에 진행 상황을 출력할지 여부.

**반환값**

- dict: 요청·응답·시간 및 대화 응답 검사를 포함한 실서버 보고서.

## `LiveLlmTester.run_agent_case`

[소스 선언](../../../../scripts/live_dialogue/tester.py#L100)

```python
def run_agent_case(self, path, name, body):
    ...
```

한 입력의 HTTP 왕복과 검사 결과를 보고서에 추가한다.

**인자**

- path: 에이전트 검사 API 경로.
- name: 보고서에 표시할 사례 이름.
- body: 대화 그래프에 전달할 요청 본문.

**반환값**

- None: 사례 결과를 보고서에 기록한다.

## `LiveLlmTester.exchange`

[소스 선언](../../../../scripts/live_dialogue/tester.py#L168)

```python
def exchange(self, rows, method, path, body=None, token=None, purpose='preparation'):
    ...
```

HTTP 요청을 보내고 왕복 기록을 남긴다.

**인자**

- rows: HTTP 왕복 기록을 추가할 목록.
- method: HTTP 요청 메서드. 예: GET, POST.
- path: 저장 파일 경로나 HTTP 요청 경로.
- body: 전송하거나 비교할 JSON 요청 본문.
- token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.
- purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

**반환값**

- dict: 성공한 HTTP 응답의 JSON 객체. 왕복 기록은 rows에도 추가한다.

## `LiveLlmTester.definitions`

[소스 선언](../../../../scripts/live_dialogue/tester.py#L186)

```python
def definitions(self, catalog):
    ...
```

사건 데이터에서 실행할 검사 사례를 구성한다.

**인자**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

**반환값**

- dict: profile, movement, evidence 세 가지 심문 사례.

## `LiveLlmTester.run_case`

[소스 선언](../../../../scripts/live_dialogue/tester.py#L197)

```python
def run_case(self, name, definition, catalog):
    ...
```

독립 수사에서 한 심문 사례를 실행하고 결과를 기록한다.

**인자**

- name: 읽을 파일 또는 실행할 사례의 이름.
- definition: 질문, 준비 자료와 기대 결과를 담은 검사 사례.
- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `LiveLlmTester.run`

[소스 선언](../../../../scripts/live_dialogue/tester.py#L210)

```python
def run(self, selected):
    ...
```

준비 조회를 한 번 수행하고 선택한 심문 사례만 실행한다.

**인자**

- selected: 실행할 실서버 검사 사례 이름 목록.

**반환값**

- dict: 선택한 사례의 검사 결과와 완료 시각을 담은 보고서.
