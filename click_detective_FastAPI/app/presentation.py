"""서버가 화면용 목록·진행률·타임라인·가능한 행동을 계산한다. 비공개 규칙은 제외한다."""

from copy import deepcopy
import math
from .result_display import RESULT_CHECK_DETAILS


class Presenter:
    """Next.js는 반환된 값을 표시한다. 진행·공개 조건을 다시 계산할 필요가 없다."""

    def __init__(self, catalog, engine):
        """같은 규칙 서비스로 UI 준비 상태와 실제 판정을 일치시킨다."""
        self.c, self.engine = catalog, engine

    def materials(self, state):
        """공개 가능한 제목·요약을 반환하고 본문·원본 파일 경로는 상세 API로 분리한다."""
        rows = []
        for record in self.c.evidence.values():
            if record["phase"] > state["phase"]:
                continue
            rows.append({key: record[key] for key in ("id", "code", "title", "type", "time", "summary", "phase")} | {
                "kind": "evidence", "archiveKind": record.get("archiveKind", "evidence"),
                "acquired": record["id"] in state["examined"], "materialKey": "evidence:" + record["id"]})
        for statement in state["statements"].values():
            rows.append({"id": statement["id"], "code": statement["code"], "title": statement["title"],
                         "kind": "testimony", "archiveKind": "testimony", "acquired": True,
                         "summary": statement["excerpt"], "speaker": statement["speaker"],
                         "materialKey": "testimony:" + statement["id"]})
        for document in state["derivedEvidence"].values():
            rows.append({key: document[key] for key in ("id", "code", "title", "summary", "phase")} | {
                "kind": "derived", "archiveKind": "inference", "acquired": True, "materialKey": "derived:" + document["id"]})
        return rows

    def describe_source(self, state, ref):
        """실제 획득 출처를 화면용 번호·제목·분류로 바꾼다."""
        if ref["kind"] == "evidence":
            item = self.c.evidence[ref["id"]]
            category = "testimony" if item.get("archiveKind") == "testimony" else "evidence"
            context = item["type"]
        elif ref["kind"] == "testimony":
            item = state["statements"][ref["id"]]
            category = "testimony"
            context = " · ".join(str(value) for value in [self.c.people[item["speaker"]]["name"], item.get("time"), item["nature"]] if value)
        else:
            item = state["derivedEvidence"][ref["id"]]
            category, context = "derived", "확보한 자료에서 도출한 추론"
        return {"ref": ref, "category": category, "code": item["code"], "title": item["title"], "context": context}

    def timeline(self, state):
        """실제 확보한 진술·문서만 공개 시간표에 추가한다. 숨겨진 실제 행적은 사용하지 않는다."""
        items = deepcopy(self.c.case["publicTimeline"])
        for statement in state["statements"].values():
            if statement.get("start") is None or not statement.get("time"):
                continue
            items.append({"id": "statement-" + statement["id"], "time": statement["time"], "start": statement["start"],
                "title": statement["title"], "text": statement["excerpt"], "category": statement["nature"],
                "statementId": statement["id"], "speaker": statement["speaker"],
                **({"end": statement["end"]} if "end" in statement else {})})
        document_events = [
            ("2-03", 2, {"id": "autopsy", "time": "22:20–23:00", "start": 1340, "end": 1380,
                "title": "검시 결과의 사망 추정 범위", "text": "뒤통수 둔기 손상이 기록되어 있습니다. 정확한 분 단위 사망 시각이나 범인을 확정하는 결과는 아닙니다.", "category": "문서·검시"}),
            ("1-05", 1, {"id": "butler-first", "time": "21:15–22:00", "start": 1275, "end": 1320,
                "title": "집사의 윤재혁 식당 목격", "text": "집사는 이 시간에 식당에서 윤재혁의 잔을 채워줬다고 증언했습니다.", "category": "진술"}),
            ("2-09", 2, {"id": "notebook-breathing", "time": "22:20", "start": 1340,
                "title": "차도윤의 수첩 기록", "text": "회장이 졸려 보였지만 고르게 숨 쉬었다는 기록입니다. 이후 상태까지 증명하지는 않습니다.", "category": "문서·검시"}),
        ]
        for key, phase, event in document_events:
            if key in state["examined"] and state["phase"] >= phase:
                items.append(event | {"evidenceId": key})
        for document in state["derivedEvidence"].values():
            related = [item for item in items if any((ref["kind"] == "testimony" and ref["id"] == item.get("statementId"))
                or (ref["kind"] == "evidence" and ref["id"] == item.get("evidenceId")) for ref in document["leafSources"])]
            if related:
                first = min(related, key=lambda item: item["start"])
                items.append({"id": document["id"], "time": first["time"], "start": first["start"], "title": document["title"],
                    "text": "관련 시간대의 자료를 연결한 수사관의 추론입니다. 새로운 목격 사실이나 확정된 감식 결과가 아닙니다.",
                    "category": "수사관 추론", "derivedId": document["id"]})
        return sorted(items, key=lambda item: (item["start"], item["id"]))

    def state(self, state):
        """명시적 공개 DTO를 구성한다. 모든 규칙·미발견 정답 후보를 반환하지 않는다."""
        safe = {key: deepcopy(state[key]) for key in ("id", "caseId", "scenarioVersion", "startedAt", "revision", "phase",
            "examined", "statements", "contradictions", "findingDetails", "derivedEvidence", "inferenceTotal",
            "revealed", "messages", "notes", "questions", "verdict")}
        counts = {"evidence": len(set(state["examined"]) & self.c.evidence.keys()),
                  "findings": min(len(set(state["contradictions"])), len(self.c.findings)),
                  "inference": min(len(state["derivedEvidence"]), len(self.c.inferences))}
        goals = {"evidence": len(self.c.evidence), "findings": len(self.c.findings), "inference": len(self.c.inferences)}
        total, complete = sum(goals.values()), sum(counts.values())
        readiness = self.engine.readiness(state)
        stage = self.c.rules["secondRound"]["requirements"]
        eligible = len(state["derivedEvidence"]) >= stage["inference"] and len(state["contradictions"]) >= stage["findings"]
        safe.update(progress={"counts": counts, "goals": goals, "completed": complete, "total": total,
            "percent": min(100, math.floor(complete / total * 100 + .5))},
            timeline=self.timeline(state), materials=self.materials(state), accusationReadiness=readiness,
            secondRoundEligibility={"inference": len(state["derivedEvidence"]), "findings": len(state["contradictions"]), "eligible": eligible},
            availableActions={"interrogate": not state["verdict"] and state["questions"] < self.c.rules["questionLimit"],
                "advance": not state["verdict"] and state["phase"] == 1 and eligible,
                "accuse": not state["verdict"],
                "notes": not state["verdict"]},
            remainingQuestions=max(0, self.c.rules["questionLimit"] - state["questions"]))
        refs = [{"kind": "evidence", "id": key} for key in self.c.evidence if key in state["examined"] and self.c.evidence[key]["phase"] <= state["phase"]]
        refs += [{"kind": "testimony", "id": key} for key in state["statements"]]
        refs += [{"kind": "derived", "id": key} for key in state["derivedEvidence"]]
        safe["inferenceSources"] = [self.describe_source(state, ref) for ref in refs]
        physical = [item for item in self.materials(state)
                    if item["kind"] == "evidence" and item["archiveKind"] == "evidence"]
        labels = {}
        for document in state["derivedEvidence"].values():
            sources = document["leafSources"]
            categories = {self.describe_source(state, ref)["category"] for ref in sources}
            labels["|".join(sorted(ref["kind"] + ":" + ref["id"] for ref in sources))] = (
                "증거·증언 교차 추론" if {"evidence", "testimony"} <= categories else
                "증언 비교 추론" if "testimony" in categories else "증거 비교 추론")
        safe["ui"] = {"requiredInferenceIds": [key for key in self.c.rules["accusation"]["requiredInferenceIds"]
                                             if key in state["derivedEvidence"]],
                      "basisLabels": labels, "physicalCount": len(physical),
                      "physicalReadCount": sum(item["acquired"] for item in physical)}
        if safe["verdict"]:
            safe["verdict"]["checkDetails"] = deepcopy(RESULT_CHECK_DETAILS)
        return safe
