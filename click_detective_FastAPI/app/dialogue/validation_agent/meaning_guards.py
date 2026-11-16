"""알려진 한국어 질문 주체 역전의 좁은 규칙 방어. 일반적인 의미 검증을 대체하지 않는다."""

import re


def has_question_actor_reversal(approved_text: str, reply: str) -> bool:
    """질문한 역할이 후보에서 질문받는 대상으로 바뀐 명시적 패턴을 탐지한다.

    예: '기자인데 ... 물었습니다' → '기자님에게 ... 질문을 했습니다'.
    한국어 전체를 해석하는 문법 분석기가 아니므로 이 패턴 밖은 의미 검증에 맡긴다.

    Args:
        approved_text (str): 모델에 사용을 허용한 사실 원문.
        reply (str): 의미를 검사하거나 문장으로 나눌 후보 대사.

    Returns:
        bool: 질문자와 행위자가 뒤바뀐 것으로 탐지되면 True.
    """
    source = re.search(
        r"(?:^|\s)([가-힣]{1,10})(?:인데|가|는)\s.*(?:물었|질문)", approved_text
    )
    if not source:
        return False
    actor = source.group(1)
    return bool(
        re.search(
            re.escape(actor)
            + r"(?:님|씨)?(?:에게|한테)\s[^.!?]*(?:질문[^.!?]*했|물었)",
            reply,
        )
    )
