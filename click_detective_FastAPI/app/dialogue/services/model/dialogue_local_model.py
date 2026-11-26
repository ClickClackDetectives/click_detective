"""Qwen 로컬 추론 실행기. 학습하지 않고 NF4 양자화 및 기존 LoRA 어댑터를 로딩한다."""

import asyncio
from time import perf_counter
from typing import Literal, Protocol

from app.dialogue.repositories.dialogue_model_file_repository import (
    validate_model_files as validate_model_files,
)
from app.dialogue.services.diagnostics.dialogue_diagnostics import trace_event
from app.dialogue.services.model.dialogue_model_loading import load_model
from app.runtime.runtime_settings import Settings

GenerationPurpose = Literal["dialogue", "verification"]


def decoding_options(settings: Settings, purpose: GenerationPurpose) -> dict:
    """대사는 표현을 샘플링하고 구조화된 질문 해석과 검증은 greedy로 실행한다.

    temperature는 다음 단어 선택의 자유도, top_p는 선택 후보의 누적 확률 범위다.
    사실 공개 권한을 늘리는 설정이 아니며 생성 후 의미 검증은 그대로 수행한다.
    검증 JSON에는 다양성이 필요 없으므로 샘플링 옵션을 전달하지 않는다.

    Args:
        settings (Settings): 모델 실행과 검색에 사용할 설정.
        purpose (GenerationPurpose): 대사 생성, 의미 검증 또는 질문 분석.

    Returns:
        dict: 대사 샘플링 또는 검증 greedy 실행 옵션.
    """
    if purpose not in {"dialogue", "verification"}:
        raise ValueError("Unknown generation purpose")
    if purpose != "dialogue" or settings.dialogue_temperature == 0:
        return {"do_sample": False}
    return {
        "do_sample": True,
        "temperature": settings.dialogue_temperature,
        "top_p": settings.dialogue_top_p,
        "repetition_penalty": settings.dialogue_repetition_penalty,
    }


class ReplyModel(Protocol):
    """실제 GPU 모델과 테스트용 가짜 모델이 공유하는 최소 인터페이스.

    Args:
        model_version (str): 응답에 표시할 모델과 어댑터의 버전 이름.

    Returns:
        ReplyModel: 위 역할을 수행하도록 생성된 객체.
    """

    model_version: str

    async def generate(
        self, messages: list[dict[str, str]], *, purpose: GenerationPurpose = "dialogue"
    ) -> str:
        """호출 목적에 맞는 디코딩으로 생성한 원본 문자열을 반환한다.

        Args:
            messages (list[dict[str, str]]): 모델에 전달할 역할별 프롬프트 목록.
            purpose (GenerationPurpose): 대사 생성, 의미 검증 또는 질문 분석.

        Returns:
            str: 호출 목적에 맞게 생성한 모델 출력 원문.
        """
        ...


class ModelContextError(ValueError):
    """승인 사실을 보존한 프롬프트가 입력 토큰 예산을 초과했다.

    Args:
        없음.

    Returns:
        ModelContextError: 위 역할을 수행하도록 생성된 객체.
    """


class LocalQwenModel:
    """프로세스당 한 번 로딩하는 4비트 Qwen과 선택적 PEFT 어댑터.

    동기 GPU 작업은 별도 스레드에서 실행한다. HTTP 요청이 취소되어도 실제 추론이
    끝날 때까지 잠금을 유지하여 GPU에 다음 추론이 겹쳐 실행되지 않게 한다.

    Args:
        settings (Settings): 모델 실행과 검색에 사용할 설정.

    Returns:
        LocalQwenModel: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, settings: Settings) -> None:
        """설정과 실행 잠금을 준비한다. 가중치는 load()에서 로딩한다.

        Args:
            settings (Settings): 모델 실행과 검색에 사용할 설정.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.settings = settings
        self.model_version = settings.local_model_version
        if settings.lora_adapter_path is not None:
            self.model_version += f"+{settings.adapter_version}"
        self._lock = asyncio.Lock()
        self.model = None
        self.tokenizer = None

    def load(self) -> None:
        """CUDA에서 NF4 + double quantization으로 로딩한다. 어댑터가 없으면 기본 모델이다.

        Args:
            없음.

        Returns:
            None: 반환값 없음.
        """
        self.model, self.tokenizer = load_model(self.settings)

    def _generate_sync(
        self, messages: list[dict[str, str]], purpose: GenerationPurpose = "dialogue"
    ) -> str:
        """Qwen 채팅 템플릿으로 추론하고 입력 토큰을 제외한 생성 부분만 디코딩한다.

        Args:
            messages (list[dict[str, str]]): 모델에 전달할 역할별 프롬프트 목록.
            purpose (GenerationPurpose): 대사 생성, 의미 검증 또는 질문 분석.

        Returns:
            str: 입력 프롬프트를 제외하고 디코딩한 생성 원문.
        """
        import torch

        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Local model has not been loaded")
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        input_length = inputs["input_ids"].shape[1]
        trace_event(
            "model_input",
            input_tokens=input_length,
            token_limit=self.settings.max_input_tokens,
            exceeds_limit=input_length > self.settings.max_input_tokens,
        )
        if input_length > self.settings.max_input_tokens:
            raise ModelContextError("Approved context exceeds local token budget")
        inputs = {name: value.to(self.model.device) for name, value in inputs.items()}
        started = perf_counter()
        options = decoding_options(self.settings, purpose)
        max_new_tokens = self.settings.max_new_tokens
        trace_event("model_decoding", purpose=purpose, **options)
        torch.cuda.reset_peak_memory_stats()
        try:
            with torch.inference_mode():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    **options,
                    use_cache=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            generated_tokens = output.shape[1] - input_length
            trace_event(
                "model_output",
                input_tokens=input_length,
                output_tokens=generated_tokens,
                reached_token_limit=generated_tokens >= max_new_tokens,
            )
            return self.tokenizer.decode(
                output[0, input_length:], skip_special_tokens=True
            )
        finally:
            trace_event(
                "model_resources",
                elapsed_ms=round((perf_counter() - started) * 1000, 2),
                allocated_bytes=torch.cuda.memory_allocated(),
                reserved_bytes=torch.cuda.memory_reserved(),
                peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                loaded_in_4bit=bool(getattr(self.model, "is_loaded_in_4bit", False)),
                quantization="nf4-double",
                adapter_enabled=self.settings.lora_adapter_path is not None,
            )

    async def generate(
        self, messages: list[dict[str, str]], *, purpose: GenerationPurpose = "dialogue"
    ) -> str:
        """GPU 추론을 직렬화한다. 취소되어도 실행 중인 스레드의 잠금은 조기에 풀지 않는다.

        Args:
            messages (list[dict[str, str]]): 모델에 전달할 역할별 프롬프트 목록.
            purpose (GenerationPurpose): 대사 생성, 의미 검증 또는 질문 분석.

        Returns:
            str: 호출 목적에 맞게 생성한 모델 출력 원문.
        """
        queued = perf_counter()
        await self._lock.acquire()
        trace_event("model_queue", wait_ms=round((perf_counter() - queued) * 1000, 2))
        task = asyncio.create_task(
            asyncio.to_thread(self._generate_sync, messages, purpose)
        )

        def release_after_completion(completed: asyncio.Task) -> None:
            """실제 GPU 작업이 끝나면 잠금을 풀고 취소 후의 예외도 회수한다.

            Args:
                completed (asyncio.Task): 실제 모델 추론이 끝난 비동기 작업.

            Returns:
                None: 반환값 없음.
            """
            self._lock.release()
            if not completed.cancelled():
                completed.exception()

        task.add_done_callback(release_after_completion)
        return await asyncio.shield(task)
