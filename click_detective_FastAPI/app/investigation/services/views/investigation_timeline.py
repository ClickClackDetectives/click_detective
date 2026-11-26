"""확보한 진술과 문서로 공개 시간표를 구성한다."""

from copy import deepcopy


def build_timeline(catalog, state):
    """실제 확보한 진술·문서만 공개 시간표에 추가한다. 숨겨진 실제 행적은 사용하지 않는다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
        state: 질문·대화·획득 자료를 담은 현재 수사 상태.

    Returns:
        list[dict]: 공개된 자료로 구성하여 시작 시각·ID 순으로 정렬한 시간표.
    """
    items = deepcopy(catalog.case["publicTimeline"])
    for statement in state["statements"].values():
        if statement.get("start") is None or not statement.get("time"):
            continue
        items.append(
            {
                "id": "statement-" + statement["id"],
                "time": statement["time"],
                "start": statement["start"],
                "title": statement["title"],
                "text": statement["excerpt"],
                "category": statement["nature"],
                "statementId": statement["id"],
                "speaker": statement["speaker"],
                **({"end": statement["end"]} if "end" in statement else {}),
            }
        )
    document_events = [
        (
            "2-03",
            2,
            {
                "id": "autopsy",
                "time": "22:20–23:00",
                "start": 1340,
                "end": 1380,
                "title": "검시 결과의 사망 추정 범위",
                "text": "뒤통수 둔기 손상이 기록되어 있습니다. 정확한 분 단위 사망 시각이나 범인을 확정하는 결과는 아닙니다.",
                "category": "문서·검시",
            },
        ),
        (
            "1-05",
            1,
            {
                "id": "butler-first",
                "time": "21:15–22:00",
                "start": 1275,
                "end": 1320,
                "title": "집사의 윤재혁 식당 목격",
                "text": "집사는 이 시간에 식당에서 윤재혁의 잔을 채워줬다고 증언했습니다.",
                "category": "진술",
            },
        ),
        (
            "2-09",
            2,
            {
                "id": "notebook-breathing",
                "time": "22:20",
                "start": 1340,
                "title": "차도윤의 수첩 기록",
                "text": "회장이 졸려 보였지만 고르게 숨 쉬었다는 기록입니다. 이후 상태까지 증명하지는 않습니다.",
                "category": "문서·검시",
            },
        ),
    ]
    for key, phase, event in document_events:
        if key in state["examined"] and state["phase"] >= phase:
            items.append(event | {"evidenceId": key})
    for document in state["derivedEvidence"].values():
        related = [
            item
            for item in items
            if any(
                (ref["kind"] == "testimony" and ref["id"] == item.get("statementId"))
                or (ref["kind"] == "evidence" and ref["id"] == item.get("evidenceId"))
                for ref in document["leafSources"]
            )
        ]
        if related:
            first = min(related, key=lambda item: item["start"])
            items.append(
                {
                    "id": document["id"],
                    "time": first["time"],
                    "start": first["start"],
                    "title": document["title"],
                    "text": "관련 시간대의 자료를 연결한 수사관의 추론입니다. 새로운 목격 사실이나 확정된 감식 결과가 아닙니다.",
                    "category": "수사관 추론",
                    "derivedId": document["id"],
                }
            )
    return sorted(items, key=lambda item: (item["start"], item["id"]))
