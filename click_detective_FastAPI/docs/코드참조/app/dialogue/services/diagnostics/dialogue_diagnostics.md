# `app/dialogue/services/diagnostics/dialogue_diagnostics.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/dialogue/services/diagnostics/dialogue_diagnostics.py)

비밀값·질문·모델 원문 없이 생성 원인을 추적하는 요청별 JSONL 진단 기록.

## `trace_event`

[소스 선언](../../../../../../app/dialogue/services/diagnostics/dialogue_diagnostics.py#L17)

```python
def trace_event(stage: str, **values) -> None:
    ...
```

현재 요청에 수치·고정 코드만 추가한다. 원문·토큰·개인정보를 전달하지 않는다.

**인자**

- stage (str): 진단 이벤트의 단계 이름.
- values: 원문이나 비밀값을 제외한 진단 수치와 고정 코드.

**반환값**

- None: 반환값 없음.

## `trace_agent_time`

[소스 선언](../../../../../../app/dialogue/services/diagnostics/dialogue_diagnostics.py#L33)

```python
def trace_agent_time(agent: str):
    ...
```

에이전트의 한 번의 호출에 걸린 시간을 기록한다.

**인자**

- agent: 그래프에 등록된 에이전트 이름.

**반환값**

- Iterator: 예외나 취소가 발생해도 종료 시점까지 측정하는 문맥.

## `start_trace`

[소스 선언](../../../../../../app/dialogue/services/diagnostics/dialogue_diagnostics.py#L53)

```python
def start_trace(request, settings) -> tuple[dict, object]:
    ...
```

실행 ID·시나리오 버전·비밀값을 제외한 유효 설정의 명시적 목록을 만든다.

**인자**

- request: 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- settings: 모델 실행과 검색에 사용할 설정.

**반환값**

- tuple[dict, object]: 새 진단 기록과 이전 요청 문맥을 복원할 토큰.

## `finish_trace`

[소스 선언](../../../../../../app/dialogue/services/diagnostics/dialogue_diagnostics.py#L101)

```python
def finish_trace(trace, token, settings, started: float) -> None:
    ...
```

진단 저장 실패로 생성 결과를 바꾸지 않고 요청 문맥을 반드시 복원한다.

**인자**

- trace: 현재 요청의 진단 정보와 이벤트 목록.
- token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.
- settings: 모델 실행과 검색에 사용할 설정.
- started (float): 실행 시작 시점의 성능 측정 타이머 값.

**반환값**

- None: 반환값 없음.
