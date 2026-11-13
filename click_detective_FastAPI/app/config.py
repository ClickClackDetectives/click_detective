"""프로젝트 기준 .env 설정. 실행 위치가 달라도 같은 데이터·모델을 사용한다."""

from pathlib import Path
from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """실행 설정. local은 실제 모델, fixture는 GPU 없는 명시적 개발·테스트 모드다."""

    model_config = SettingsConfigDict(env_prefix="CLICK_", env_file=PROJECT_ROOT / ".env", extra="ignore")
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
    # 대사만 샘플링한다. 0은 기존 greedy 방식이며 검증 JSON은 항상 greedy다.
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

    @field_validator("database_path", "data_dir", "local_model_path", "lora_adapter_path", "diagnostics_path", mode="before")
    @classmethod
    def project_path(cls, value):
        """상대 경로와 ~를 해석한다. 모델 파일은 자동 다운로드하지 않는다."""
        if value is None:
            return None
        path = Path(value).expanduser()
        return path if path.is_absolute() else PROJECT_ROOT / path
