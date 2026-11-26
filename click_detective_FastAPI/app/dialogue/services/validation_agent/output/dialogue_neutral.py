"""질문에 드러난 주제에 맞춰 검증에 사용할 고정 중립 대사를 선택한다."""

import re
import unicodedata

from app.dialogue.dto.dialogue_reply_dto import CharacterReplyRequest

NO_APPROVAL_REPLY = "그 부분에 대해서는 말씀드릴 내용이 없습니다."
UNVERIFIED_REPLIES = (
    "그 질문에는 지금 답변드리기 어렵습니다.",
    "그 부분은 지금 말씀드리기 어려워요.",
    "그 점에 대해서는 지금 답하기가 어렵네요.",
    "지금은 그 질문에 대해 드릴 수 있는 답이 없습니다.",
)
NEUTRAL_REPLIES = {
    "timeline": (
        "그 시간대에 관해서는 드릴 말씀이 없어요.",
        "시간에 관해서는 제가 덧붙일 말이 없습니다.",
        "그 시각에 대해서는 말씀드릴 내용이 없습니다.",
    ),
    "whereabouts": (
        "어디에 있었는지에 대해서는 덧붙일 말이 없습니다.",
        "동선에 관해서는 드릴 말씀이 없어요.",
        "장소에 대해서는 제가 더 말씀드릴 내용이 없습니다.",
    ),
    "people": (
        "그 인물에 관해서는 드릴 말씀이 없어요.",
        "누구였는지에 대해서는 덧붙일 말이 없습니다.",
        "인물에 관해서는 제가 더 말씀드릴 내용이 없습니다.",
    ),
    "relationships": (
        "그 관계에 대해서는 드릴 말씀이 없어요.",
        "서로 어떤 사이였는지에 대해 덧붙일 말은 없습니다.",
        "관계에 대해서는 제가 더 말씀드릴 내용이 없습니다.",
    ),
    "evidence": (
        "그 자료에 관해서는 드릴 말씀이 없어요.",
        "그 자료에 대해서는 제가 덧붙일 말이 없습니다.",
        "자료에 관해서는 더 설명드릴 내용이 없습니다.",
    ),
    "observations": (
        "무엇을 보거나 들었는지에 대해서는 덧붙일 말이 없습니다.",
        "목격 여부에 관해서는 드릴 말씀이 없어요.",
        "그때 무엇을 알아차렸는지에 대해서는 더 말씀드릴 내용이 없습니다.",
    ),
    "communications": (
        "연락에 관해서는 드릴 말씀이 없어요.",
        "무슨 대화가 있었는지에 대해서는 덧붙일 말이 없습니다.",
        "연락 여부에 대해서는 제가 더 말씀드릴 내용이 없습니다.",
    ),
    "actions": (
        "당시 행동에 관해서는 드릴 말씀이 없어요.",
        "무엇을 했는지에 대해서는 덧붙일 말이 없습니다.",
        "그 행동에 대해 더 말씀드릴 내용이 없습니다.",
    ),
    "motives": (
        "그 이유에 관해서는 드릴 말씀이 없어요.",
        "왜 그랬는지에 대해서는 제가 덧붙일 말이 없습니다.",
        "동기에 관해서는 더 말씀드릴 내용이 없습니다.",
    ),
    "speculation": (
        "그 가능성에 관해서는 드릴 말씀이 없어요.",
        "그 가정에 대해서는 덧붙일 말이 없습니다.",
        "그 부분을 추측해서 말씀드리기는 어렵습니다.",
    ),
    "out_of_scope": (
        "그 질문에는 답변드리기 어렵습니다. 사건에 관해 궁금한 점이 있으면 말씀해 주세요.",
        "그 요청에는 답변드리기 어려워요. 이번 사건에 관한 질문을 해 주세요.",
        "그 부분에는 드릴 말씀이 없습니다. 사건 이야기로 돌아가도 될까요?",
    ),
    "general": (
        NO_APPROVAL_REPLY,
        "그 질문에 관해서는 드릴 말씀이 없어요.",
        "그 부분에 대해서는 제가 덧붙일 말이 없습니다.",
    ),
}

# 범위 밖 요청은 시간이나 자료 표현이 함께 등장해도 우선한다.
OUT_OF_SCOPE = re.compile(
    r"(?:미공개|비공개|숨겨\s*둔|숨겨진|공개\s*되지\s*않은)\s*(?:단서|증거|자료|정보|진술)"
    r"|(?:시스템\s*(?:프롬프트|지시|메시지)|이전\s*지시|내부\s*설정)"
    r"|(?:저녁|점심|아침)\s*메뉴.{0,15}(?:추천|골라)"
    r"|(?:수학\s*문제|숙제).{0,15}(?:풀어|해\s*줘)"
    r"|(?:농담|유머).{0,15}(?:해\s*줘|들려)"
    r"|(?:주식|코인|영화|맛집).{0,15}(?:추천|골라)"
)
TOPIC_PATTERNS = {
    "timeline": r"언제|몇\s*시|시각|시간대|오전|오후|새벽|아침|저녁|어젯밤",
    "whereabouts": r"어디|동선|알리바이|장소|이동|어느\s*길",
    "people": r"누구|누가|어느\s*분|어떤\s*사람|인상착의",
    "relationships": r"관계|어떤\s*사이|무슨\s*사이|친분|아는\s*사람",
    "evidence": r"자료|증거|사진|녹음|영상|기록|영수증|문서|cctv|지문",
    "observations": r"목격|봤|보았|보셨|들었|들으셨|알아차",
    "communications": r"연락|전화|통화|문자|메시지|대화|무슨\s*말",
    "actions": r"뭘\s*했|무엇을\s*했|뭐\s*했|행동|무슨\s*일을\s*했",
    "motives": r"왜|동기|이유|목적",
    "speculation": r"추측|가설|가능성|만약|혹시라도|것\s*같",
}
TOPIC_PATTERNS = {
    topic: re.compile(pattern) for topic, pattern in TOPIC_PATTERNS.items()
}


def classify_neutral_question(question: str) -> str:
    """질문에서 직접 언급한 주제를 찾는다.

    Args:
        question: 플레이어 질문 원문.

    Returns:
        str: 수사 범위 밖, 단일 주제 또는 공통 문구 카테고리.
    """
    normalized = unicodedata.normalize("NFKC", question).casefold()
    if OUT_OF_SCOPE.search(normalized):
        return "out_of_scope"

    topics = [
        topic for topic, pattern in TOPIC_PATTERNS.items() if pattern.search(normalized)
    ]
    if len(topics) == 1:
        return topics[0]
    return "general"


def select_neutral_reply(request: CharacterReplyRequest) -> tuple[str, str]:
    """승인 여부와 질문에 맞춰 같은 요청에는 같은 고정 대사를 고른다.

    Args:
        request: 질문, 승인 사실과 재시도 식별자를 담은 요청.

    Returns:
        tuple[str, str]: 중립 카테고리와 선택한 대사.
    """
    if request.allowed_facts:
        category = "unverified"
        replies = UNVERIFIED_REPLIES
    else:
        category = classify_neutral_question(request.question)
        replies = NEUTRAL_REPLIES[category]

    index = request.request_id.int % len(replies)
    return category, replies[index]
