"""심문 대상에게 제시한 자료와 새로 공개할 쟁점을 고른다."""


def collect_materials(planner, state, command):
    """과거와 현재의 제시 자료를 중복 없이 모으고 원본 출처를 확인한다.

    Args:
        planner: 자료의 획득 조건을 확인할 승인 계획 담당자.
        state: 현재 수사의 대화와 획득 자료 정보.
        command: 대상 인물과 이번에 제시한 자료를 담은 심문 입력.

    Returns:
        tuple: 원본 증거 ID 집합과 제시 자료의 출처 목록.
    """
    material_ids = []
    for message in state["messages"]:
        if message["suspectId"] != command.suspect_id:
            continue
        material_id = message.get("evidenceId")
        if material_id and material_id not in material_ids:
            material_ids.append(material_id)
    if command.material_id and command.material_id not in material_ids:
        material_ids.append(command.material_id)

    physical_ids = set()
    sources = []
    for material_id in material_ids:
        references = planner.expand_material(state, material_id)
        for reference in references:
            if reference["kind"] == "evidence":
                physical_ids.add(reference["id"])
        if material_id in state["derivedEvidence"]:
            kind = "derived"
        else:
            kind = "evidence"
        sources.append({"kind": kind, "id": material_id})
    return physical_ids, sources


def collect_findings(catalog, state, command, physical_ids):
    """이번 자료 제시로 새롭게 공개할 수 있는 쟁점을 고른다.

    Args:
        catalog: 인물별 쟁점 규칙을 가진 사건 데이터.
        state: 이미 공개된 쟁점을 담은 수사 상태.
        command: 대상 인물과 현재 제시 자료를 담은 심문 입력.
        physical_ids: 실제 획득한 제시 자료의 원본 증거 ID 집합.

    Returns:
        list[dict]: 아직 공개되지 않았고 근거 조건이 충족된 쟁점 규칙.
    """
    findings = []
    if not command.material_id:
        return findings
    for rule in catalog.findings:
        if rule["suspectId"] != command.suspect_id:
            continue
        if rule["flag"] in state["revealed"]:
            continue
        has_all_evidence = True
        for evidence_id in rule["need"]:
            if evidence_id not in physical_ids:
                has_all_evidence = False
        if has_all_evidence:
            findings.append(rule)
    return findings
