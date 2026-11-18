"""수사에서 획득한 증거의 열람과 출처 기반 추론을 처리한다."""

from copy import deepcopy

from fastapi import HTTPException


def examine(catalog, state, command):
    """현재 단계의 실제 자료만 열람한다. 중복은 개수·revision을 늘리지 않는다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
        state: 질문·대화·획득 자료를 담은 현재 수사 상태.
        command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

    Returns:
        dict: 열람 처리한 원본 자료의 식별자.
    """
    record = catalog.evidence.get(command.evidence_id)
    if not record or record["phase"] > state["phase"]:
        raise HTTPException(404, "현재 공개된 자료가 아닙니다.")
    if record["id"] not in state["examined"]:
        state["examined"].append(record["id"])
    return {"material_id": record["id"]}


def readable_source(catalog, state, source):
    """존재뿐 아니라 실제 획득·단계 조건도 검사한다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
        state: 질문·대화·획득 자료를 담은 현재 수사 상태.
        source: 열람 가능 여부를 검사할 자료 종류와 식별자.

    Returns:
        None: 출처 열람 조건을 확인한다. 미획득 자료면 HTTPException을 낸다.
    """
    kind, key = source["kind"], source["id"]
    if kind == "evidence":
        record = catalog.evidence.get(key)
        known = (
            record and record["phase"] <= state["phase"] and key in state["examined"]
        )
    else:
        known = key in state["statements" if kind == "testimony" else "derivedEvidence"]
    if not known:
        raise HTTPException(422, "직접 열람하거나 생성한 자료만 연결할 수 있습니다.")


def infer(catalog, state, command):
    """직접 선택한 정확한 조합과 단계가 일치하면 고정 결론을 만든다. LLM은 사용하지 않는다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
        state: 질문·대화·획득 자료를 담은 현재 수사 상태.
        command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

    Returns:
        dict: 확보한 출처 조합으로 만든 추론 문서의 사본.
    """
    sources = []
    for source in command.sources:
        sources.append(source.model_dump())
    keys = set()
    for ref in sources:
        keys.add((ref["kind"], ref["id"]))
    if len(keys) != len(sources):
        raise HTTPException(422, "서로 다른 자료를 선택하세요.")
    for source in sources:
        readable_source(catalog, state, source)
    rule = next(
        (
            rule
            for rule in catalog.inferences
            if {(ref["kind"], ref["id"]) for ref in rule["sources"]} == keys
        ),
        None,
    )
    if not rule:
        raise HTTPException(422, "선택한 자료만으로 뒷받침되는 연결을 찾지 못했습니다.")
    if rule["phase"] != state["phase"]:
        raise HTTPException(422, "이 추론의 조사 단계를 확인하세요.")
    key = "derived-" + rule["id"]
    if key not in state["derivedEvidence"]:
        leaves = {}
        for ref in sources:
            if ref["kind"] == "derived":
                refs = state["derivedEvidence"][ref["id"]]["leafSources"]
            else:
                refs = [ref]
            for leaf in refs:
                leaves[(leaf["kind"], leaf["id"])] = deepcopy(leaf)
        state["derivedEvidence"][key] = {
            "id": key,
            "code": rule["code"],
            "kind": "derived",
            "type": "추론 증거",
            "title": rule["title"],
            "time": "",
            "summary": "확보한 자료의 연결로 도출한 수사관의 추론입니다.",
            "phase": state["phase"],
            "body": rule["body"],
            "sourceRefs": sources,
            "leafSources": list(leaves.values()),
            "investigationPhase": rule["phase"],
            "construction": "chain"
            if any(ref["kind"] == "derived" for ref in sources)
            else "base",
        }
    return deepcopy(state["derivedEvidence"][key])
