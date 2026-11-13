# app/dialogue/diagnostics.py 상세 설명

[문서 목차](../../../README.md) · [파일별 목차](../../README.md) · [현재 소스](../../../../app/dialogue/diagnostics.py)

## 역할과 읽는 순서

비밀값·질문·모델 원문 없이 생성 원인을 추적하는 요청별 JSONL 진단 기록.

현재 pipeline_version은 semantic-paraphrase-v7입니다. model_decoding·토큰·NF4·어댑터·메모리·거절 코드를 기록하며 진단에 키와 대사 원문을 넣지 않습니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## 모듈 설정과 상수

```python
PIPELINE_VERSION = "semantic-paraphrase-v7"
CURRENT_TRACE: ContextVar[dict | None] = ContextVar("generation_trace", default=None)
logger = logging.getLogger(__name__)
```

이 값은 코드 선언입니다. 실제 .env 비밀값이나 수사 DB 값은 여기에 읽어 넣지 않았습니다.

## trace_event

[원본 16번째 줄](../../../../app/dialogue/diagnostics.py#L16)

현재 요청에 수치·고정 코드만 추가한다. 원문·토큰·개인정보를 전달하지 않는다.

### 입력과 처리

```python
def trace_event(stage: str, **values) -> None:
```

주요 분기 조건은 `trace is not None`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def trace_event(stage: str, **values) -> None:
    """현재 요청에 수치·고정 코드만 추가한다. 원문·토큰·개인정보를 전달하지 않는다."""
    trace = CURRENT_TRACE.get()
    if trace is not None:
        trace["events"].append({"stage": stage, **values})
````

## start_trace

[원본 23번째 줄](../../../../app/dialogue/diagnostics.py#L23)

실행 ID·시나리오 버전·비밀값을 제외한 유효 설정의 명시적 목록을 만든다.

### 입력과 처리

```python
def start_trace(request, settings) -> tuple[dict, object]:
```

### 실제 코드

````python
def start_trace(request, settings) -> tuple[dict, object]:
    """실행 ID·시나리오 버전·비밀값을 제외한 유효 설정의 명시적 목록을 만든다."""
    trace = {
        "run_id": str(uuid4()), "request_id": str(request.request_id),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "scenario_version": request.scenario_version, "case_id": request.case_id,
        "pipeline_version": PIPELINE_VERSION, "events": [],
        "settings": {key: getattr(settings, key) for key in (
            "generation_mode", "generation_output_format", "local_model_version", "adapter_version", "rag_enabled", "rag_top_k",
            "max_input_tokens", "max_new_tokens", "history_limit", "generation_attempts",
            "verification_attempts", "verification_batch_size", "timeout_seconds", "fallback_on_error",
            "dialogue_temperature", "dialogue_top_p", "dialogue_repetition_penalty")},
    }
    return trace, CURRENT_TRACE.set(trace)
````

## finish_trace

[원본 39번째 줄](../../../../app/dialogue/diagnostics.py#L39)

진단 저장 실패로 생성 결과를 바꾸지 않고 요청 문맥을 반드시 복원한다.

### 입력과 처리

```python
def finish_trace(trace, token, settings, started: float) -> None:
```

주요 분기 조건은 `not settings.diagnostics_enabled`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def finish_trace(trace, token, settings, started: float) -> None:
    """진단 저장 실패로 생성 결과를 바꾸지 않고 요청 문맥을 반드시 복원한다."""
    CURRENT_TRACE.reset(token)
    trace["completed_at"] = datetime.now(timezone.utc).isoformat()
    trace["elapsed_ms"] = round((perf_counter() - started) * 1000, 2)
    if not settings.diagnostics_enabled:
        return
    try:
        settings.diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
        with settings.diagnostics_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(trace, ensure_ascii=False) + "\n")
    except OSError:
        logger.warning("Generation diagnostics could not be written")
````

