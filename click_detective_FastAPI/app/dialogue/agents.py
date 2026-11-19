"""이전 DialogueAgents 이름을 사용하는 코드를 위한 연결이다."""

from .inference_agent.agent import InferenceAgent
from .preprocess_agent.agent import PreprocessAgent


class DialogueAgents:
    """전처리와 생성 담당자에게 요청을 전달한다.

    Args:
        settings: 전처리와 생성 설정.
        model: 생성에 사용할 모델.

    Returns:
        DialogueAgents: 기존 호출 이름을 제공하는 객체.
    """

    def __init__(self, settings, model):
        """두 단계의 담당자를 준비한다.

        Args:
            settings: 전처리와 생성 설정.
            model: 생성에 사용할 모델.

        Returns:
            None: 담당 객체를 보관한다.
        """
        self.preprocessor = PreprocessAgent(settings)
        self.generator = InferenceAgent(settings, model)

    async def preprocess_agent(self, state):
        """전처리 담당자에게 현재 작업을 전달한다.

        Args:
            state: 현재 요청의 작업 상태.

        Returns:
            dict: 생성에 사용할 자료와 초기 시도 횟수.
        """
        return await self.preprocessor.preprocess_agent(state)

    async def inference_agent(self, state):
        """생성 담당자에게 현재 작업을 전달한다.

        Args:
            state: 현재 요청의 작업 상태.

        Returns:
            dict: 후보 대사 또는 실행 오류 상태.
        """
        return await self.generator.inference_agent(state)
