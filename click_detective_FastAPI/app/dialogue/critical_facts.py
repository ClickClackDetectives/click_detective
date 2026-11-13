"""명시적 수량·시각 귀속·일부 목적 표현의 규칙 검사. 일반 의미 이해를 대신하지 않는다.

정규식으로 읽을 수 있는 범위만 다룬다. 생략·동의어가 애매하면 검증 불가로 거절할
수 있으므로 원래 승인 의미를 유지한 재서술을 회귀 평가로 함께 확인해야 한다.
"""

import re

from .schemas import CharacterReplyRequest
from .semantic_verification import candidate_sentences
from .verification_units import build_verification_units

NATIVE_NUMBERS = {"한": 1, "두": 2, "세": 3, "네": 4, "다섯": 5, "여섯": 6,
                  "일곱": 7, "여덟": 8, "아홉": 9, "열": 10}
COUNT = re.compile(r"(?<![가-힣0-9])([0-9]+|한|두|세|네|다섯|여섯|일곱|여덟|아홉|열)\s*(알|억(?:\s*원)?|년|점|명|개)")
CLOCK = re.compile(r"(?<!\d)(\d{1,2})(?:\s*시(?:\s*(\d{1,2})\s*분)?|:(\d{2}))")


def quantity_anchors(text: str) -> set[tuple[int, str]]:
    """두 알과 2알 등을 같은 값으로 읽는다. 모든 한국어 수사를 해석하지는 않는다."""
    return {(int(number) if number.isdigit() else NATIVE_NUMBERS[number], re.sub(r"\s+", "", unit).replace("억원", "억"))
            for number, unit in COUNT.findall(text)}


def time_anchors(text: str) -> set[tuple[int, int]]:
    """11시 2분·23:02의 시계상 위치를 비교한다. 오전/오후 추론은 모델에 남긴다."""
    return {(int(hour) % 12, int(korean or colon or 0)) for hour, korean, colon in CLOCK.findall(text)}


def time_actions(text: str) -> set[tuple[tuple[int, int], str]]:
    """같은 문장에 명시된 숨기기·방문 행동과 시각을 연결한다. 문장 밖 추론은 하지 않는다."""
    result = set()
    for part in candidate_sentences(text):
        actions = set()
        if re.search(r"숨[기겼겨긴]|감[추췄춘춰]", part.text):
            actions.add("hide")
        if re.search(r"(?:서재|방|현장)(?:에|로)\s*(?:갔|왔|찾아|들어)|방문", part.text):
            actions.add("visit")
        result.update((clock, action) for clock in time_anchors(part.text) for action in actions)
    return result


def postponement_target(text: str) -> str | None:
    """발표·공개·일정·회의를 미루려는 명시적 목적 표현만 읽는다."""
    if not re.search(r"(?:미루|늦추|연기하|지연시키)(?:려|기\s*위해|고자)", text):
        return None
    match = re.search(r"발표|공개|일정|회의", text)
    return match.group() if match else None


def critical_claim_error(request: CharacterReplyRequest, reply: str) -> str | None:
    """원문에 없는 명시적 수량·시각·행동 귀속과 읽을 수 있는 필수 목적 누락을 거절한다.

    새 사건 사실의 근거는 allowed_facts뿐이다. 질문·인물 프로필·제시 자료·이력에서
    숫자나 행동을 가져왔다고 승인하지 않는다. 오류에는 원문을 넣지 않는다.
    """
    approved = " ".join(fact.text for fact in request.allowed_facts)
    if not quantity_anchors(reply).issubset(quantity_anchors(approved)):
        return "unapproved_quantity_claim"
    if not time_anchors(reply).issubset(time_anchors(approved)):
        return "unapproved_time_claim"
    if not time_actions(reply).issubset(time_actions(approved)):
        return "time_action_binding_changed"
    for container in ("병", "잔"):
        negative = re.search(re.escape(container) + r"(?:에|에는|에도)\s*넣지\s*않", approved)
        positive = re.search(re.escape(container) + r"(?:에|에는|에도)\s*넣었", reply)
        if negative and positive:
            return "container_negation_changed"
    required = set(request.required_fact_ids)
    for unit in build_verification_units(request):
        if unit.fact_id not in required:
            continue
        if not predicate_anchors(unit.text).issubset(predicate_anchors(reply)):
            return "required_action_or_limit_missing"
        target = postponement_target(unit.text)
        if target and not any(postponement_target(part.text) == target for part in candidate_sentences(reply)):
            return "required_purpose_unverified"
        if not time_actions(unit.text).issubset(time_actions(reply)):
            return "required_time_action_missing"
    return None


def critical_evidence_error(unit_text: str, evidence_text: str) -> str | None:
    """모델이 true라고 해도 선택한 실제 근거에서 명시적 수량·시각이 빠지면 거절한다."""
    if not predicate_anchors(unit_text).issubset(predicate_anchors(evidence_text)):
        return "evidence_action_or_limit_missing"
    if not quantity_anchors(unit_text).issubset(quantity_anchors(evidence_text)):
        return "evidence_quantity_missing"
    if not time_anchors(unit_text).issubset(time_anchors(evidence_text)):
        return "evidence_time_missing"
    if not time_actions(unit_text).issubset(time_actions(evidence_text)):
        return "evidence_time_action_missing"
    target = postponement_target(unit_text)
    if target and not any(postponement_target(part.text) == target for part in candidate_sentences(evidence_text)):
        return "evidence_purpose_unverified"
    return None


def predicate_anchors(text: str) -> set[str]:
    """방문·회수 의도·관찰 한계·흔들기·무반응·맥 확인 한계·질문의 명시적 표현을 읽는다.

    알려진 누락 사례를 위한 제한된 표현 사전이며 한국어 전체의 논리 분석은 아니다.
    같은 문장 안의 주체나 시제까지 완전하게 보장하지 않는다.
    """
    result = set()
    for part in candidate_sentences(text):
        sentence = part.text
        if re.search(r"(?:서재|방|현장|금고)(?:에|로)[^.!?]*(?:갔|왔|다녀|들어)|방문", sentence):
            result.add("visit")
        if re.search(r"가지러|찾으러|회수하러|가져오려|되찾으려", sentence):
            result.add("retrieve_intent")
        if re.search(r"(?:상태|모습)[^.!?]*(?:확신|확인|판단)[^.!?]*(?:못|않)", sentence):
            result.add("observation_uncertain")
        if re.search(r"흔들", sentence):
            result.add("shake")
        if re.search(r"반응[^.!?]*(?:없|않)|응답[^.!?]*없", sentence):
            result.add("no_response")
        if re.search(r"(?:맥|맥박)[^.!?]*(?:못|확실하지|불확실)", sentence):
            result.add("pulse_uncertain")
        if re.search(r"물었|물어봤|질문[^.!?]*했|여쭤봤|여쭈었", sentence):
            result.add("question")
    return result
