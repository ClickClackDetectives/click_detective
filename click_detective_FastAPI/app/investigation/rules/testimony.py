"""승인된 심문 결과를 대화·쟁점·진술 기록에 반영한다."""

from copy import deepcopy


def record_plan(catalog, state, plan, response):
    """질문 차감 후 검증된 응답으로 대화·쟁점·진술을 일괄 반영한다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
        state: 질문·대화·획득 자료를 담은 현재 수사 상태.
        plan: 게임 규칙이 승인한 사실과 기록 예정 정보를 담은 계획.
        response: 검사하거나 저장할 최종 대사 응답.

    Returns:
        dict: 기록한 대사, 종료 사유, 모델 버전과 사용 사실 ID.
    """
    state["messages"].extend(
        [
            {
                "suspectId": plan.suspect_id,
                "role": "user",
                "text": plan.question,
                "evidenceId": plan.material_id,
                "topicId": plan.topic,
            },
            {
                "suspectId": plan.suspect_id,
                "role": "suspect",
                "text": response.reply,
                "finishReason": response.finish_reason,
                "modelVersion": response.model_version,
            },
        ]
    )
    incomplete = response.finish_reason in {"partial", "neutral"}
    delivered = set(response.used_fact_ids)
    for rule in plan.new_findings:
        entry = catalog.testimony["admissionEntries"].get(rule["flag"])
        key = entry["key"] if entry else "finding-" + rule["flag"]
        if incomplete and f"{plan.suspect_id}-{key}" not in delivered:
            continue
        if rule["flag"] not in state["revealed"]:
            state["revealed"].append(rule["flag"])
            state["contradictions"].append(rule["label"])
            state["findingDetails"].append(
                {
                    "title": rule["label"],
                    "suspectId": plan.suspect_id,
                    "sourceRefs": plan.sources,
                    "messageIndex": len(state["messages"]) - 1,
                }
            )
    for entry in plan.entries:
        if entry["key"] == "profile":
            continue
        key = plan.suspect_id + "-" + entry["key"]
        if key in state["statements"] or (incomplete and key not in delivered):
            continue
        topic = entry.get("_topic", plan.topic)
        section = (
            "다른 사람들에 대해"
            if (topic or "").startswith("about-")
            else "그날 밤 당신의 행동"
        )
        script = catalog.scripts["characters"][plan.suspect_id]
        excerpt = response._verified_finding_excerpts.get(key, entry["text"])
        state["statements"][key] = {
            "id": key,
            "code": f"ST-{len(state['statements']) + 1:03}",
            "speaker": plan.suspect_id,
            "topic": "admission" if plan.new_findings else topic or "movement",
            "title": entry["title"],
            "excerpt": excerpt,
            "nature": entry["nature"],
            "sourceRefs": deepcopy(plan.sources),
            "messageIndex": len(state["messages"]) - 1,
            "source": {
                "file": "01_대본_" + catalog.people[plan.suspect_id]["name"] + ".pdf",
                "pages": script["sections"][section]["pages"],
                "section": section,
            },
            **{
                field: deepcopy(entry[field])
                for field in ("target", "time", "start", "end", "supersedes")
                if field in entry
            },
        }
    return {
        "reply": response.reply,
        "finish_reason": response.finish_reason,
        "model_version": response.model_version,
        "used_fact_ids": response.used_fact_ids,
    }
