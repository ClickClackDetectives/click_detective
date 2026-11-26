"""CUDA에 양자화 모델과 토크나이저를 불러온다."""

from app.dialogue.repositories.dialogue_model_file_repository import (
    validate_model_files,
)


def load_model(settings):
    """CUDA에서 NF4 + double quantization으로 로딩한다. 어댑터가 없으면 기본 모델이다.

    Args:
        settings: 모델 실행과 검색에 사용할 설정.

    Returns:
        tuple: CUDA에 불러온 4비트 모델과 해당 모델의 토크나이저.
    """
    validate_model_files(settings)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    if not torch.cuda.is_available():
        raise RuntimeError("Local NF4 mode requires a working CUDA GPU")
    compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        str(settings.local_model_path),
        local_files_only=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        str(settings.local_model_path),
        local_files_only=True,
        quantization_config=quantization,
        device_map={"": 0},
        torch_dtype=compute_dtype,
        attn_implementation="sdpa",
    )
    if not getattr(model, "is_loaded_in_4bit", False):
        raise RuntimeError("The model must be loaded in 4-bit NF4 mode")
    if settings.lora_adapter_path is not None:
        from peft import PeftModel

        model = PeftModel.from_pretrained(
            model,
            str(settings.lora_adapter_path),
            local_files_only=True,
            is_trainable=False,
        )
    model.eval()
    return model, tokenizer
