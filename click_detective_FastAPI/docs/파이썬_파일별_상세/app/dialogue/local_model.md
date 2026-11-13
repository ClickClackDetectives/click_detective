# app/dialogue/local_model.py 상세 설명

[문서 목차](../../../README.md) · [파일별 목차](../../README.md) · [현재 소스](../../../../app/dialogue/local_model.py)

## 역할과 읽는 순서

Qwen 로컬 추론 실행기. 학습하지 않고 NF4 양자화 및 기존 LoRA 어댑터를 로딩한다.

NF4 4-bit·double quantization으로 Qwen을 로딩하고 기존 어댑터를 추론용으로 적용합니다. dialogue만 샘플링하며 verification은 greedy입니다. 학습은 하지 않습니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## 모듈 설정과 상수

```python
GenerationPurpose = Literal["dialogue", "verification"]
```

이 값은 코드 선언입니다. 실제 .env 비밀값이나 수사 DB 값은 여기에 읽어 넣지 않았습니다.

## decoding_options

[원본 14번째 줄](../../../../app/dialogue/local_model.py#L14)

대사는 표현을 샘플링하고 검증은 greedy로 실행한다.

temperature는 다음 단어 선택의 자유도, top_p는 선택 후보의 누적 확률 범위다.
사실 공개 권한을 늘리는 설정이 아니며 생성 후 의미 검증은 그대로 수행한다.
검증 JSON에는 다양성이 필요 없으므로 샘플링 옵션을 전달하지 않는다.

### 입력과 처리

```python
def decoding_options(settings: Settings, purpose: GenerationPurpose) -> dict:
```

주요 분기 조건은 `purpose not in {'dialogue', 'verification'}`, `purpose == 'verification' or settings.dialogue_temperature == 0`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def decoding_options(settings: Settings, purpose: GenerationPurpose) -> dict:
    """대사는 표현을 샘플링하고 검증은 greedy로 실행한다.

    temperature는 다음 단어 선택의 자유도, top_p는 선택 후보의 누적 확률 범위다.
    사실 공개 권한을 늘리는 설정이 아니며 생성 후 의미 검증은 그대로 수행한다.
    검증 JSON에는 다양성이 필요 없으므로 샘플링 옵션을 전달하지 않는다.
    """
    if purpose not in {"dialogue", "verification"}:
        raise ValueError("Unknown generation purpose")
    if purpose == "verification" or settings.dialogue_temperature == 0:
        return {"do_sample": False}
    return {"do_sample": True, "temperature": settings.dialogue_temperature,
            "top_p": settings.dialogue_top_p,
            "repetition_penalty": settings.dialogue_repetition_penalty}
````

## ReplyModel

[원본 30번째 줄](../../../../app/dialogue/local_model.py#L30)

실제 GPU 모델과 테스트용 가짜 모델이 공유하는 최소 인터페이스.

### 선언 필드

```python
model_version: str
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## ReplyModel.generate

[원본 35번째 줄](../../../../app/dialogue/local_model.py#L35)

호출 목적에 맞는 디코딩으로 생성한 원본 문자열을 반환한다.

### 입력과 처리

```python
async def generate(self, messages: list[dict[str, str]], *, purpose: GenerationPurpose = "dialogue") -> str:
```

async 함수이므로 호출자는 await로 결과를 기다립니다. 대기 중 다른 요청이 실행될 수 있어 revision과 잠금 처리가 필요합니다.

### 실제 코드

````python
async def generate(self, messages: list[dict[str, str]], *, purpose: GenerationPurpose = "dialogue") -> str:
        """호출 목적에 맞는 디코딩으로 생성한 원본 문자열을 반환한다."""
        ...
````

## ModelContextError

[원본 40번째 줄](../../../../app/dialogue/local_model.py#L40)

승인 사실을 보존한 프롬프트가 입력 토큰 예산을 초과했다.

## validate_model_files

[원본 44번째 줄](../../../../app/dialogue/local_model.py#L44)

로컬 모델 및 선택한 어댑터 파일의 존재를 확인한다. 네트워크 다운로드는 하지 않는다.

### 입력과 처리

```python
def validate_model_files(settings: Settings) -> None:
```

주요 분기 조건은 `not any(((model_path / name).is_file() for name in ('model.safetensors.index.json', 'model.safetensors', 'pytorch_model.bin.index.json', 'pytorch_model.bin')))`, `settings.lora_adapter_path is not None`, `not (model_path / filename).is_file()`, `not (adapter_path / 'adapter_config.json').is_file() or not has_weights`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def validate_model_files(settings: Settings) -> None:
    """로컬 모델 및 선택한 어댑터 파일의 존재를 확인한다. 네트워크 다운로드는 하지 않는다."""
    model_path = settings.local_model_path
    for filename in ("config.json", "tokenizer_config.json"):
        if not (model_path / filename).is_file():
            raise ValueError(f"Missing local model file: {filename}")
    if not any((model_path / name).is_file() for name in ("model.safetensors.index.json", "model.safetensors", "pytorch_model.bin.index.json", "pytorch_model.bin")):
        raise ValueError("Local model weights are missing")
    if settings.lora_adapter_path is not None:
        adapter_path = settings.lora_adapter_path
        has_weights = any((adapter_path / name).is_file() for name in (
            "adapter_model.safetensors", "adapter_model.bin",
        ))
        if not (adapter_path / "adapter_config.json").is_file() or not has_weights:
            raise ValueError("LoRA adapter configuration or weights are missing")
````

## LocalQwenModel

[원본 61번째 줄](../../../../app/dialogue/local_model.py#L61)

프로세스당 한 번 로딩하는 4비트 Qwen과 선택적 PEFT 어댑터.

동기 GPU 작업은 별도 스레드에서 실행한다. HTTP 요청이 취소되어도 실제 추론이
끝날 때까지 잠금을 유지하여 GPU에 다음 추론이 겹쳐 실행되지 않게 한다.

## LocalQwenModel.__init__

[원본 68번째 줄](../../../../app/dialogue/local_model.py#L68)

설정과 실행 잠금을 준비한다. 가중치는 load()에서 로딩한다.

### 입력과 처리

```python
def __init__(self, settings: Settings) -> None:
```

주요 분기 조건은 `settings.lora_adapter_path is not None`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def __init__(self, settings: Settings) -> None:
        """설정과 실행 잠금을 준비한다. 가중치는 load()에서 로딩한다."""
        self.settings = settings
        self.model_version = settings.local_model_version
        if settings.lora_adapter_path is not None:
            self.model_version += f"+{settings.adapter_version}"
        self._lock = asyncio.Lock()
        self.model = None
        self.tokenizer = None
````

## LocalQwenModel.load

[원본 78번째 줄](../../../../app/dialogue/local_model.py#L78)

CUDA에서 NF4 + double quantization으로 로딩한다. 어댑터가 없으면 기본 모델이다.

### 입력과 처리

```python
def load(self) -> None:
```

주요 분기 조건은 `not torch.cuda.is_available()`, `not getattr(self.model, 'is_loaded_in_4bit', False)`, `self.settings.lora_adapter_path is not None`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def load(self) -> None:
        """CUDA에서 NF4 + double quantization으로 로딩한다. 어댑터가 없으면 기본 모델이다."""
        validate_model_files(self.settings)
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
        self.tokenizer = AutoTokenizer.from_pretrained(
            str(self.settings.local_model_path), local_files_only=True,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            str(self.settings.local_model_path),
            local_files_only=True,
            quantization_config=quantization,
            device_map={"": 0},
            torch_dtype=compute_dtype,
            attn_implementation="sdpa",
        )
        if not getattr(self.model, "is_loaded_in_4bit", False):
            raise RuntimeError("The model must be loaded in 4-bit NF4 mode")
        if self.settings.lora_adapter_path is not None:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(
                self.model, str(self.settings.lora_adapter_path),
                local_files_only=True, is_trainable=False,
            )
        self.model.eval()
````

## LocalQwenModel._generate_sync

[원본 114번째 줄](../../../../app/dialogue/local_model.py#L114)

Qwen 채팅 템플릿으로 추론하고 입력 토큰을 제외한 생성 부분만 디코딩한다.

### 입력과 처리

```python
def _generate_sync(self, messages: list[dict[str, str]], purpose: GenerationPurpose = "dialogue") -> str:
```

주요 분기 조건은 `self.model is None or self.tokenizer is None`, `input_length > self.settings.max_input_tokens`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def _generate_sync(self, messages: list[dict[str, str]], purpose: GenerationPurpose = "dialogue") -> str:
        """Qwen 채팅 템플릿으로 추론하고 입력 토큰을 제외한 생성 부분만 디코딩한다."""
        import torch
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Local model has not been loaded")
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
        )
        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        input_length = inputs["input_ids"].shape[1]
        trace_event("model_input", input_tokens=input_length, token_limit=self.settings.max_input_tokens,
                    exceeds_limit=input_length > self.settings.max_input_tokens)
        if input_length > self.settings.max_input_tokens:
            raise ModelContextError("Approved context exceeds local token budget")
        inputs = {name: value.to(self.model.device) for name, value in inputs.items()}
        started = perf_counter()
        options = decoding_options(self.settings, purpose)
        trace_event("model_decoding", purpose=purpose, **options)
        torch.cuda.reset_peak_memory_stats()
        try:
            with torch.inference_mode():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=self.settings.max_new_tokens,
                    **options,
                    use_cache=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            generated_tokens = output.shape[1] - input_length
            trace_event("model_output", input_tokens=input_length, output_tokens=generated_tokens,
                        reached_token_limit=generated_tokens >= self.settings.max_new_tokens)
            return self.tokenizer.decode(output[0, input_length:], skip_special_tokens=True)
        finally:
            trace_event("model_resources", elapsed_ms=round((perf_counter()-started)*1000, 2),
                        allocated_bytes=torch.cuda.memory_allocated(), reserved_bytes=torch.cuda.memory_reserved(),
                        peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                        peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                        loaded_in_4bit=bool(getattr(self.model, "is_loaded_in_4bit", False)),
                        quantization="nf4-double", adapter_enabled=self.settings.lora_adapter_path is not None)
````

## LocalQwenModel.generate

[원본 154번째 줄](../../../../app/dialogue/local_model.py#L154)

GPU 추론을 직렬화한다. 취소되어도 실행 중인 스레드의 잠금은 조기에 풀지 않는다.

### 입력과 처리

```python
async def generate(self, messages: list[dict[str, str]], *, purpose: GenerationPurpose = "dialogue") -> str:
```

async 함수이므로 호출자는 await로 결과를 기다립니다. 대기 중 다른 요청이 실행될 수 있어 revision과 잠금 처리가 필요합니다.

주요 분기 조건은 `not completed.cancelled()`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
async def generate(self, messages: list[dict[str, str]], *, purpose: GenerationPurpose = "dialogue") -> str:
        """GPU 추론을 직렬화한다. 취소되어도 실행 중인 스레드의 잠금은 조기에 풀지 않는다."""
        queued = perf_counter()
        await self._lock.acquire()
        trace_event("model_queue", wait_ms=round((perf_counter()-queued)*1000, 2))
        task = asyncio.create_task(asyncio.to_thread(self._generate_sync, messages, purpose))

        def release_after_completion(completed: asyncio.Task) -> None:
            """실제 GPU 작업이 끝나면 잠금을 풀고 취소 후의 예외도 회수한다."""
            self._lock.release()
            if not completed.cancelled():
                completed.exception()

        task.add_done_callback(release_after_completion)
        return await asyncio.shield(task)
````

