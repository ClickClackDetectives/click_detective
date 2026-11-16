"""사건 데이터에서 실서버 대화 검사 입력을 고른다."""

import json

from .errors import LiveTestFailure


def definitions(catalog, data_dir):
    """현재 프로젝트의 인물·주제·1차 단일 근거 쟁점으로 3가지 입력을 구성한다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
        data_dir: 사건 JSON 데이터가 있는 디렉터리.

    Returns:
        dict: profile, movement, evidence 세 가지 심문 사례.
    """
    people = catalog["characters"]
    person = people[0]
    movement = next(
        (
            item
            for item in people
            if any(topic["id"] == "movement" for topic in item["interviewTopics"])
        ),
        None,
    )
    if movement is None:
        raise LiveTestFailure("카탈로그에 동선 심문 주제가 없습니다.")
    topic = next(
        item for item in movement["interviewTopics"] if item["id"] == "movement"
    )
    evidence = json.loads(
        (data_dir / "case/evidence.json").read_text(encoding="utf-8")
    )["records"]
    rules = json.loads(
        (data_dir / "case/findings.private.json").read_text(encoding="utf-8")
    )["rules"]
    initial_ids = {item["id"] for item in evidence if item["phase"] == 1}
    finding = next(
        (
            item
            for item in rules
            if len(item["need"]) == 1
            and set(item["need"]) <= initial_ids
            and item["suspectId"] in {p["id"] for p in people}
        ),
        None,
    )
    if finding is None:
        raise LiveTestFailure("내부 사건 데이터에 1차 단일 근거 심문 항목이 없습니다.")
    return {
        "profile": {
            "description": "짧은 자기소개: 승인된 인물 정보로 생성·검증",
            "fields": {"suspect_id": person["id"], "question": "자기소개를 해주세요."},
            "evidence_ids": [],
        },
        "movement": {
            "description": "동선 주제: 여러 승인 문장의 생성·검증",
            "fields": {
                "suspect_id": movement["id"],
                "question": topic["question"],
                "topic_id": topic["id"],
            },
            "evidence_ids": [],
        },
        "evidence": {
            "description": "자료 제시: 획득 근거로 인정 대사 생성·검증",
            "fields": {
                "suspect_id": finding["suspectId"],
                "question": "제시한 자료의 경위를 설명하세요.",
                "material_id": finding["need"][0],
            },
            "evidence_ids": finding["need"],
            "expected_finding": finding["label"],
        },
    }
