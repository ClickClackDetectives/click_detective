"""LangGraph 생성·검증 호출을 재현하는 모의 모델이다."""

import json


class ApprovedModel:
    """승인 원문을 사용해 LangGraph의 생성·검증 호출을 재현하는 모의 모델.

    Args:
        없음.

    Returns:
        ApprovedModel: 위 역할을 수행하도록 생성된 객체.
    """

    model_version = "runtime-contract-model"

    def __init__(self):
        """호출 횟수로 생성과 별도 검증이 실제 실행됐는지 확인한다.

        Args:
            없음.

        Returns:
            None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.
        """
        self.calls = []

    async def generate(self, messages, *, purpose="dialogue"):
        """생성은 승인 원문을 연결하고 추가 모델 판정에서는 불확실한 문장을 보류한다.

        Args:
            messages: 모델에 전달할 역할별 프롬프트 목록.
            purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

        Returns:
            str: 호출 목적에 맞게 생성한 모델 출력 원문.
        """
        context = json.loads(messages[1]["content"])
        self.calls.append(context)
        if purpose == "dialogue":
            return " ".join(fact["text"] for fact in context["approved_facts"])
        if "public_sources" in context:
            return json.dumps({"allowed": False})
        return json.dumps({"matches": []})
