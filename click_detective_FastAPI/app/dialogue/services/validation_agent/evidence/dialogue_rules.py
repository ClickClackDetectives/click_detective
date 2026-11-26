"""문장 코사인 유사도와 근거 검사 규칙."""

import re
import unicodedata
from pathlib import Path
from threading import Lock

from app.dialogue.services.validation_agent.evidence.dialogue_critical_facts import (
    critical_evidence_error,
)
from app.dialogue.services.validation_agent.evidence.dialogue_meaning_guards import (
    has_question_actor_reversal,
)
from app.dialogue.services.validation_agent.output.dialogue_neutral import (
    NO_APPROVAL_REPLY,
)
from app.dialogue.services.validation_agent.sentences.dialogue_semantic_verification import (
    candidate_sentences,
)
from app.runtime.runtime_settings import PROJECT_ROOT

NEUTRAL_PROMPTS = frozenset(
    {
        NO_APPROVAL_REPLY,
        "어떤 시간대를 말씀하시는 건가요?",
        "어떤 부분을 말씀하시는 건가요?",
        "질문을 조금 더 구체적으로 말씀해 주시겠어요?",
    }
)
CORE_MARKERS = (
    r"않|아니|못|없|본 적 없",
    r"들었|전해|전언|다고 하더|라고 하더|대요|래요",
    r"직접|목격|제가 봤|제가 보았",
    r"추측|아마|같아요|같습니다|듯|확실하지",
    r"오전|아침|새벽",
    r"오후|저녁|낮|밤",
)
CONTEXTUAL_AFFIRMATION = re.compile(
    r"^(?:네|예|맞아요|맞습니다|그렇습니다)(?:[\s,.!?]|$)"
)


def normalize(text: str) -> str:
    """공백과 문장 끝 마침표를 정리한다.

    Args:
        text: 비교할 대사나 승인 사실.

    Returns:
        str: 비교용 문자열.
    """
    return " ".join(unicodedata.normalize("NFC", text).casefold().split()).rstrip(".。")


class SentenceTransformerSimilarity:
    """요청에 포함된 문장들을 한 배치로 임베딩한다.

    Args:
        model_name: 로컬 모델 경로 또는 캐시에 준비된 모델 ID.
        device: 임베딩 실행 장치.

    Returns:
        SentenceTransformerSimilarity: 서버 프로세스에서 공유할 유사도 계산기.
    """

    def __init__(self, model_name: str, device: str):
        """로컬 모델과 추론 잠금을 준비한다.

        Args:
            model_name: 모델 ID 또는 프로젝트 기준 상대 경로.
            device: 임베딩 실행 장치.

        Returns:
            None: 모델을 한 번 로드한다.
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise RuntimeError(
                "SentenceTransformer 검증을 사용하려면 .[embeddings] 의존성을 설치하세요."
            ) from error

        path = Path(model_name).expanduser()
        if model_name.startswith("."):
            path = PROJECT_ROOT / path
        source = str(path) if path.is_absolute() else model_name
        try:
            self.model = SentenceTransformer(
                source, device=device, local_files_only=True, trust_remote_code=False
            )
        except OSError as error:
            raise RuntimeError(
                "SentenceTransformer 모델을 불러올 수 없습니다. 모델을 미리 내려받거나 "
                "CLICK_VALIDATION_EMBEDDING_MODEL에 로컬 모델 경로를 지정하세요."
            ) from error
        self.lock = Lock()

    def scores(self, candidates: list[str], approved: list[str]):
        """정규화한 문장 벡터의 내적으로 코사인 유사도 행렬을 계산한다.

        Args:
            candidates: 생성된 후보 문장 목록.
            approved: 승인 사실의 검증 단위 목록.

        Returns:
            ndarray: 후보 문장 행과 승인 단위 열로 구성한 유사도 행렬.
        """
        texts = list(dict.fromkeys(candidates + approved))
        indexes = {text: index for index, text in enumerate(texts)}
        with self.lock:
            vectors = self.model.encode(
                texts, normalize_embeddings=True, show_progress_bar=False
            )
        left = vectors[[indexes[text] for text in candidates]]
        right = vectors[[indexes[text] for text in approved]]
        return left @ right.T


def preserves_anchors(source: str, candidate: str) -> bool:
    """코드가 인식할 수 있는 중요 사실의 누락·변경을 거절한다.

    Args:
        source: 근거가 되는 승인 사실 또는 공개 진술.
        candidate: 검증할 생성 문장.

    Returns:
        bool: 양방향 중요 사실 검사와 주체·양태 검사를 통과하면 True.
    """
    if normalize(source) == normalize(candidate):
        return True
    if any(
        bool(re.search(pattern, source)) != bool(re.search(pattern, candidate))
        for pattern in CORE_MARKERS
    ):
        return False
    if re.findall(r"\d+", source) != re.findall(r"\d+", candidate):
        return False
    return not (
        critical_evidence_error(source, candidate)
        or critical_evidence_error(candidate, source)
        or has_question_actor_reversal(source, candidate)
    )


def rule_match(source: str, candidate: str) -> bool:
    """연결 어미 뒤 쉼표와 제한된 한국어 종결어미 차이를 허용한다.

    Args:
        source: 승인 원문 또는 공개 진술.
        candidate: 비교할 후보 문장.

    Returns:
        bool: 정규화한 문장이 같거나 허용된 어미 변화만 있으면 True.
    """

    def stem(text):
        """연결 어미 뒤 쉼표와 제한된 말투 차이를 정리한다.

        Args:
            text: 정규화할 문장.

        Returns:
            str: 쉼표와 말투 차이를 정리한 문자열.
        """
        normalized = normalize(text).replace("예약해 둔", "예약한")
        normalized = re.sub(r"(고|지만),\s+", r"\1 ", normalized)
        normalized = re.sub(r"수령하러(?=\s)", "받으러", normalized)
        return re.sub(r"(했|왔|갔|봤|들었)(?:어요|습니다)$", r"\1", normalized)

    return stem(source) == stem(candidate) and preserves_anchors(source, candidate)


def public_sources(request, history_limit: int) -> list[str]:
    """같은 인물에게 공개된 프로필과 이전 답변을 읽는다.

    Args:
        request: 현재 질문과 공개 프로필, 대화 이력.
        history_limit: 참조 가능한 최근 이력 수.

    Returns:
        list[str]: 질문자의 추측을 제외한 공개 답변 근거.
    """
    name = request.persona.name
    role = request.persona.role
    history = request.history[-history_limit:] if history_limit else []
    return [
        f"제 이름은 {name}입니다.",
        f"저는 {role}입니다.",
        f"저는 {role} {name}입니다.",
        *(
            part.text
            for message in history
            if message.role == "suspect"
            for part in candidate_sentences(message.text)
            if not CONTEXTUAL_AFFIRMATION.match(part.text)
        ),
    ]
