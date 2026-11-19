"""실제 인물과 사건 자료로 130개 질문을 구성한다."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / ".reports/llm-api-130-live.json"
DOCUMENT = ROOT.parent / "click_detective_검증_에이전트_입력출력_예시_130선.md"
BACKUP = ROOT.parent / "click_detective_검증_에이전트_내부검사_모의예시_원본.md"


def definitions(catalog):
    """실제 인물·주제·추천 질문·1차 자료를 이용해 인물당 26개를 만든다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

    Returns:
        list[dict]: 인물별 질문과 준비 자료로 구성한 130개 실행 사례.
    """
    evidence = json.loads((ROOT / "data/case/evidence.json").read_text())["records"]
    rules = json.loads((ROOT / "data/case/findings.private.json").read_text())["rules"]
    initial = [e for e in evidence if e["phase"] == 1]
    initial_ids = {e["id"] for e in initial}
    output = []
    for person in catalog["characters"]:
        own_rules = [
            r
            for r in rules
            if r["suspectId"] == person["id"] and set(r["need"]) <= initial_ids
        ]
        acquired = sorted({item for r in own_rules for item in r["need"]})

        def add(category, question, topic=None, material=None):
            """현재 인물의 질문과 준비 자료를 검사 입력 목록에 추가한다.

            Args:
                category: 조회할 자료 분류.
                question: 사용자가 입력한 질문 원문.
                topic: 질문에서 명시할 주제 식별자.
                material: 예시 질문에 제시할 자료 식별자.

            Returns:
                None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
            """
            fields = {"suspect_id": person["id"], "question": question}
            if topic:
                fields["topic_id"] = topic
            if material:
                fields["material_id"] = material
            output.append(
                {
                    "description": f"{person['name']} · {category}",
                    "fields": fields,
                    "evidence_ids": list(
                        dict.fromkeys(acquired + ([material] if material else []))
                    ),
                    "category": category,
                }
            )

        for q in [
            "자기소개를 해주세요.",
            "회장님과 어떤 관계인지 본인의 입장에서 설명해 주세요.",
            "오늘 이곳에 온 이유와 맡고 있는 일을 말씀해 주세요.",
        ]:
            add("인물 소개", q)
        for q in [
            "그날 밤 면담 전후의 동선과 직접 본 일을 말씀해 주세요.",
            "오늘 밤 어디에서 무엇을 했는지 시간 순서대로 말씀해 주세요.",
            "기억하는 시각과 행동을 구분하고 확실히 보지 못한 일도 알려주세요.",
            "면담 이후의 행적을 설명하고 추측을 직접 목격한 일처럼 말하지 말아 주세요.",
        ]:
            add("동선과 관찰 한계", q, "movement")
        for topic in [t for t in person["interviewTopics"] if t["id"] != "movement"]:
            add("다른 인물에 대한 진술", topic["question"], topic["id"])
            add(
                "다른 인물에 대한 진술 재질문",
                topic["question"] + " 직접 본 내용과 모르는 내용을 구분해 주세요.",
                topic["id"],
            )
        for q in person["suggestions"]:
            add("원본 추천 질문", q)
        related = [e for e in initial if e["id"] in acquired]
        chosen = (related + [e for e in initial if e not in related])[:8]
        for e in chosen:
            add(
                "자료 한 개 제시",
                f"'{e['title']}' 자료를 제시합니다. 이 자료와 본인의 관계 및 알고 있는 경위를 설명해 주세요.",
                material=e["id"],
            )
    assert len(output) == 130, len(output)
    return output
