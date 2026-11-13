# app/config.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../app/config.py)

## 역할과 읽는 순서

프로젝트 기준 .env 설정. 실행 위치가 달라도 같은 데이터·모델을 사용한다.

CLICK_ 환경변수와 프로젝트 .env를 읽습니다. 실제 키는 문서에 싣지 않습니다. 경로는 프로젝트 기준으로 해석하며 변경 후 서버를 재시작합니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## 모듈 설정과 상수

```python
PROJECT_ROOT = Path(__file__).resolve().parents[1]
```

이 값은 코드 선언입니다. 실제 .env 비밀값이나 수사 DB 값은 여기에 읽어 넣지 않았습니다.

## Settings

[원본 11번째 줄](../../../app/config.py#L11)

실행 설정. local은 실제 모델, fixture는 GPU 없는 명시적 개발·테스트 모드다.

### 선언 필드

```python
api_key: str = Field(min_length=16)
database_path: Path = PROJECT_ROOT / ".data/games.sqlite3"
data_dir: Path = PROJECT_ROOT / "data"
generation_mode: Literal["local", "fixture"] = "local"
local_model_path: Path = PROJECT_ROOT / "models/Qwen2.5-7B-Instruct"
local_model_version: str = "Qwen2.5-7B-Instruct-nf4"
lora_adapter_path: Path | None = PROJECT_ROOT / "adapters/best_adapter"
adapter_version: str = "provided-adapter"
generation_output_format: Literal["text", "json"] = "text"
max_input_tokens: int = Field(default=2048, ge=128, le=8192)
max_new_tokens: int = Field(default=512, ge=32, le=2048)
dialogue_temperature: float = Field(default=0.65, ge=0, le=1.5, allow_inf_nan=False)
dialogue_top_p: float = Field(default=0.9, gt=0, le=1, allow_inf_nan=False)
dialogue_repetition_penalty: float = Field(default=1.05, ge=1, le=1.5, allow_inf_nan=False)
timeout_seconds: float = Field(default=90, gt=0, le=180)
fallback_on_error: bool = True
generation_attempts: int = Field(default=2, ge=1, le=3)
verification_attempts: int = Field(default=2, ge=1, le=3)
verification_batch_size: int = Field(default=10, ge=1, le=10)
rag_enabled: bool = True
rag_top_k: int = Field(default=3, ge=0, le=10)
history_limit: int = Field(default=6, ge=0, le=20)
diagnostics_enabled: bool = True
diagnostics_path: Path = PROJECT_ROOT / ".data/dialogue-traces.jsonl"
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Settings.project_path

[원본 43번째 줄](../../../app/config.py#L43)

상대 경로와 ~를 해석한다. 모델 파일은 자동 다운로드하지 않는다.

### 입력과 처리

```python
def project_path(cls, value):
```

주요 분기 조건은 `value is None`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def project_path(cls, value):
        """상대 경로와 ~를 해석한다. 모델 파일은 자동 다운로드하지 않는다."""
        if value is None:
            return None
        path = Path(value).expanduser()
        return path if path.is_absolute() else PROJECT_ROOT / path
````

