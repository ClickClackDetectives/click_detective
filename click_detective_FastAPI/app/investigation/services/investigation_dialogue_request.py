"""승인된 사실과 저장 상태를 모델에 전달할 입력으로 변환한다."""

from app.dialogue.dto.dialogue_reply_dto import CharacterReplyRequest


def prepare_interrogation(service, state, command):
    """수사 상태와 심문 입력을 검사하고 차감 전 모델 요청을 준비한다.

    Args:
        service: 진행 규칙, 승인 계획과 모델 요청 구성을 담당하는 서비스.
        state: 질문을 차감하기 전 수사 상태.
        command: 서버에 전송한 심문 명령.

    Returns:
        tuple: 승인 계획, 모델 요청과 자유 질문 검색 여부.
    """
    service.engine.require_active(state)
    search_free = service.settings.rag_enabled and service.search_free
    plan = service.planner.prepare(state, command, search_free=search_free)
    return plan, service.dialogue_request(state, command, plan), search_free


# 쟁점의 승인 대사에서 발견을 직접 뒷받침하는 문장 위치다. 첫 문장은 0이다.
FINDING_CORE_SENTENCES = {
    "gang_drug": (0,),
    "gang_visit": (0, 3),
    "yoon_money": (0,),
    "yoon_visit": (0,),
    "sera_draft": (0,),
    "cha_identity": (0,),
    "seo_forgery": (0,),
    "seo_burn": (1,),
    "weapon_fit": (0,),
    "witness_gap": (1,),
}


def dialogue_request(catalog, history_limit, state, command, plan):
    """수사 상태와 승인 계획으로 대화 요청을 만든다.

    Args:
        catalog: 사건 데이터와 인물 말투를 제공하는 객체.
        history_limit: 전송할 최근 메시지 수. 0이면 대화 이력을 생략한다.
        state: 현재 수사의 내부 상태.
        command: 사용자의 심문 명령.
        plan: 규칙이 승인한 사실과 진술 계획.

    Returns:
        CharacterReplyRequest: 승인 사실, 최근 대화와 쟁점별 내부 검증 기준을 담은 입력.
    """
    required_ids = []
    for fact in plan.facts:
        required_ids.append(fact["id"])
    history = []
    if history_limit:
        for message in state["messages"]:
            if message["suspectId"] == plan.suspect_id:
                history.append({"role": message["role"], "text": message["text"]})
        history = history[-history_limit:]
    person = catalog.people[plan.suspect_id]
    speech_style = person.get("speech_style")
    if not isinstance(speech_style, str) or not speech_style.strip():
        speech_style = "존댓말. 승인 원문의 말투와 관찰 한계를 유지하세요."
    request = CharacterReplyRequest(
        request_id=command.request_id,
        game_id=state["id"],
        case_id=catalog.case_id,
        scenario_version=catalog.version,
        state_revision=state["revision"],
        turn_index=state["questions"] + 1,
        suspect_id=plan.suspect_id,
        phase=state["phase"],
        question=plan.question,
        topic_id=plan.topic,
        persona={
            "name": person["name"],
            "role": person["role"],
            "speech_style": speech_style,
        },
        allowed_facts=plan.facts,
        required_fact_ids=required_ids,
        history=history,
    )
    if plan.new_findings:
        for finding, fact in zip(plan.new_findings, plan.facts, strict=True):
            core = FINDING_CORE_SENTENCES.get(finding["flag"])
            if core:
                request._finding_core_sentences[fact["id"]] = core
    return request
