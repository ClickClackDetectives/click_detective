"""대화 모델과 어댑터의 로컬 파일을 확인한다."""

from app.runtime.runtime_settings import Settings


def validate_model_files(settings: Settings) -> None:
    """로컬 모델 및 선택한 어댑터 파일의 존재를 확인한다. 네트워크 다운로드는 하지 않는다.

    Args:
        settings (Settings): 모델 실행과 검색에 사용할 설정.

    Returns:
        None: 반환값 없음.
    """
    model_path = settings.local_model_path
    for filename in ("config.json", "tokenizer_config.json"):
        if not (model_path / filename).is_file():
            raise ValueError(f"Missing local model file: {filename}")
    if not any(
        (model_path / name).is_file()
        for name in (
            "model.safetensors.index.json",
            "model.safetensors",
            "pytorch_model.bin.index.json",
            "pytorch_model.bin",
        )
    ):
        raise ValueError("Local model weights are missing")
    if settings.lora_adapter_path is not None:
        adapter_path = settings.lora_adapter_path
        has_weights = any(
            (adapter_path / name).is_file()
            for name in (
                "adapter_model.safetensors",
                "adapter_model.bin",
            )
        )
        if not (adapter_path / "adapter_config.json").is_file() or not has_weights:
            raise ValueError("LoRA adapter configuration or weights are missing")
