"""InferenceAgent의 처리 순서를 담는다."""

import asyncio
import json
from time import perf_counter

from fastapi import HTTPException

from ..diagnostics import trace_event
from ..local_model import ModelContextError
from ..reply_validation import assemble_reply
from ..state import InterrogationState


class InferenceAgent:
    """모델에 후보 대사 생성을 요청한다.

    Args:
        settings: 검색과 생성 실행에 사용할 설정.
        model: 대사 생성에 사용할 공용 모델. 전처리에서는 직접 호출하지 않는다.

    Returns:
        InferenceAgent: 해당 단계의 작업을 수행하는 객체.
    """

    def __init__(self, settings, model):
        """사용할 의존성과 초기 상태를 준비한다.

        Args:
            settings: 모델 실행과 검색에 사용할 설정.
            model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.settings = settings
        self.model = model

    async def inference_agent(self, state: InterrogationState) -> dict:
        """에이전트 2: 사실의 의미를 유지하며 표현을 샘플링한다. 원문 복사를 요구하지 않는다.

        Args:
            state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

        Returns:
            dict: 후보 대사와 시도 횟수 또는 실행 오류 상태.
        """
        request = state["request"]
        if not request.allowed_facts:
            trace_event("empty_approval", policy="deterministic_neutral", model_calls=0)
            reply = assemble_reply(request)
            if self.settings.generation_output_format == "json":
                raw_output = json.dumps({"reply": reply})
            else:
                raw_output = reply
            return {
                "attempt": 0,
                "raw_output": raw_output,
                "error_status": None,
                "retry": False,
            }
        messages = list(state["messages"])
        if state.get("rejection_code"):
            if self.settings.generation_output_format == "text":
                output_rule = "캐릭터 대사 원문만 출력하고 JSON·해설은 쓰지 마세요."
            else:
                output_rule = "reply를 담은 JSON 객체 하나만 출력하세요."
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"이전 시도 검증 코드: {state['rejection_code']}. "
                        "required_sentences는 복사할 정답이 아니라 보존할 의미 목록입니다. "
                        "행동·시각·부정·관찰 한계는 유지하되 문장 구성과 표현은 자연스럽게 바꾸세요. "
                        "특히 시각 누락 오류이면 해당 시각과 연결된 행동을 함께 명시하세요. "
                        + output_rule
                    ),
                }
            )
        result = {
            "attempt": state.get("attempt", 0) + 1,
            "error_status": None,
            "retry": False,
        }
        try:
            async with asyncio.timeout(self.settings.timeout_seconds):
                started = perf_counter()
                raw = await self.model.generate(messages, purpose="dialogue")
                trace_event(
                    "generation",
                    attempt=result["attempt"],
                    elapsed_ms=round((perf_counter() - started) * 1000, 2),
                )
            result["raw_output"] = raw
            return result
        except ModelContextError:
            raise HTTPException(
                422, "Approved context exceeds local token budget"
            ) from None
        except TimeoutError:
            result["error_status"] = 504
            return result
        except (RuntimeError, ValueError):
            result["error_status"] = 502
            return result
