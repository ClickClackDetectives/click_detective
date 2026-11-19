"""획득한 출처를 화면에서 선택할 수 있는 설명으로 바꾼다."""


def describe_source(catalog, state, ref):
    """실제 획득 출처를 화면용 번호·제목·분류로 바꾼다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
        state: 질문·대화·획득 자료를 담은 현재 수사 상태.
        ref: 자료 종류와 식별자를 담은 출처 참조.

    Returns:
        dict: 출처의 번호·제목·분류와 설명.
    """
    if ref["kind"] == "evidence":
        item = catalog.evidence[ref["id"]]
        if item.get("archiveKind") == "testimony":
            category = "testimony"
        else:
            category = "evidence"
        context = item["type"]
    elif ref["kind"] == "testimony":
        item = state["statements"][ref["id"]]
        category = "testimony"
        context = " · ".join(
            str(value)
            for value in [
                catalog.people[item["speaker"]]["name"],
                item.get("time"),
                item["nature"],
            ]
            if value
        )
    else:
        item = state["derivedEvidence"][ref["id"]]
        category, context = "derived", "확보한 자료에서 도출한 추론"
    return {
        "ref": ref,
        "category": category,
        "code": item["code"],
        "title": item["title"],
        "context": context,
    }


def list_materials(catalog, state):
    """현재 수사에서 볼 수 있는 원본·진술·추론의 목록을 만든다.

    Args:
        catalog: 원본 증거를 담은 사건 데이터.
        state: 현재 조사 단계와 획득 자료를 담은 수사 상태.

    Returns:
        list[dict]: 화면에 공개할 자료의 제목·요약·획득 여부.
    """
    rows = []
    fields = ["id", "code", "title", "type", "time", "summary", "phase"]
    for record in catalog.evidence.values():
        if record["phase"] > state["phase"]:
            continue
        item = {}
        for field in fields:
            item[field] = record[field]
        item["kind"] = "evidence"
        item["archiveKind"] = record.get("archiveKind", "evidence")
        item["acquired"] = record["id"] in state["examined"]
        item["materialKey"] = "evidence:" + record["id"]
        rows.append(item)
    for statement in state["statements"].values():
        item = {
            "id": statement["id"],
            "code": statement["code"],
            "title": statement["title"],
            "kind": "testimony",
            "archiveKind": "testimony",
            "acquired": True,
            "summary": statement["excerpt"],
            "speaker": statement["speaker"],
            "materialKey": "testimony:" + statement["id"],
        }
        rows.append(item)
    for document in state["derivedEvidence"].values():
        item = {}
        for field in ["id", "code", "title", "summary", "phase"]:
            item[field] = document[field]
        item["kind"] = "derived"
        item["archiveKind"] = "inference"
        item["acquired"] = True
        item["materialKey"] = "derived:" + document["id"]
        rows.append(item)
    return rows
