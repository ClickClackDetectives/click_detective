"""승인된 사실과 저장 상태를 모델에 전달할 입력으로 변환한다."""

from ..dialogue.schemas import CharacterReplyRequest


def dialogue_request(catalog, history_limit, state, command, plan):
    """수사 상태와 승인 계획으로 대화 요청을 만든다.

    Args:
        catalog: 사건 데이터와 인물 말투를 제공하는 객체.
        history_limit: 전송할 최근 메시지 수. 0이면 대화 이력을 생략한다.
        state: 현재 수사의 내부 상태.
        command: 사용자의 심문 명령.
        plan: 규칙이 승인한 사실과 진술 계획.

    Returns:
        CharacterReplyRequest: 승인 사실과 최근 대화를 담은 모델 입력.
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
    return CharacterReplyRequest(
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
