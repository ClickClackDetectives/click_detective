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
        """생성은 평문, 검증은 후보 문장 번호를 갖는 엄격한 JSON으로 응답한다.

        Args:
            messages: 모델에 전달할 역할별 프롬프트 목록.
            purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

        Returns:
            str: 호출 목적에 맞게 생성한 모델 출력 원문.
        """
        context = json.loads(messages[1]["content"])
        self.calls.append(context)
        if "candidate_sentences" not in context:
            return " ".join(fact["text"] for fact in context["approved_facts"])
        sources = {
            unit["index"]: unit["text"]
            for fact in context["approved_facts"]
            for unit in fact["units"]
        }
        return json.dumps(
            {
                "checks": [
                    [
                        unit["index"],
                        True,
                        [
                            part["id"]
                            for part in context["candidate_sentences"]
                            if sources[unit["index"]] in part["text"]
                        ],
                    ]
                    for unit in context["verification_units"]
                ],
                "has_contradiction": False,
                "has_unsupported_claims": False,
                "history_consistent": True,
                "persona_consistent": True,
                "uncertain": False,
            }
        )
