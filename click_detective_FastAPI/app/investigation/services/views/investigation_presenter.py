"""서버가 화면용 목록·진행률·타임라인·가능한 행동을 계산한다. 비공개 규칙은 제외한다."""

import math
from copy import deepcopy

from app.investigation.services.views.investigation_material_display import (
    describe_source,
    list_materials,
)
from app.investigation.services.views.investigation_result_display import (
    RESULT_CHECK_DETAILS,
)
from app.investigation.services.views.investigation_timeline import build_timeline


class Presenter:
    """Next.js는 반환된 값을 표시한다. 진행·공개 조건을 다시 계산할 필요가 없다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
        engine: 게임 진행과 행동의 조건을 판정하는 객체.

    Returns:
        Presenter: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, catalog, engine):
        """같은 규칙 서비스로 UI 준비 상태와 실제 판정을 일치시킨다.

        Args:
            catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
            engine: 게임 진행과 행동의 조건을 판정하는 객체.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.catalog = catalog
        self.engine = engine

    def materials(self, state):
        """공개 가능한 제목·요약을 반환하고 본문·원본 파일 경로는 상세 API로 분리한다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.

        Returns:
            list[dict]: 현재 공개 가능한 원본·진술·추론의 제목과 요약 목록.
        """
        return list_materials(self.catalog, state)

    def describe_source(self, state, ref):
        """실제 획득 출처를 화면용 번호·제목·분류로 바꾼다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            ref: 자료 종류와 식별자를 담은 출처 참조.

        Returns:
            dict: 출처의 번호·제목·분류와 설명.
        """
        return describe_source(self.catalog, state, ref)

    def timeline(self, state):
        """실제 확보한 진술·문서만 공개 시간표에 추가한다. 숨겨진 실제 행적은 사용하지 않는다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.

        Returns:
            list[dict]: 공개된 자료로 구성하여 시작 시각·ID 순으로 정렬한 시간표.
        """
        return build_timeline(self.catalog, state)

    def state(self, state):
        """명시적 공개 DTO를 구성한다. 모든 규칙·미발견 정답 후보를 반환하지 않는다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.

        Returns:
            dict: 내부 비공개 규칙을 제외한 화면용 수사 상태.
        """
        safe = {}
        fields = [
            "id",
            "caseId",
            "scenarioVersion",
            "startedAt",
            "revision",
            "phase",
            "examined",
            "statements",
            "contradictions",
            "findingDetails",
            "derivedEvidence",
            "inferenceTotal",
            "revealed",
            "messages",
            "notes",
            "questions",
            "verdict",
        ]
        for field in fields:
            safe[field] = deepcopy(state[field])

        evidence_count = 0
        for evidence_id in self.catalog.evidence:
            if evidence_id in state["examined"]:
                evidence_count += 1
        counts = {
            "evidence": evidence_count,
            "findings": min(
                len(set(state["contradictions"])), len(self.catalog.findings)
            ),
            "inference": min(
                len(state["derivedEvidence"]), len(self.catalog.inferences)
            ),
        }
        goals = {
            "evidence": len(self.catalog.evidence),
            "findings": len(self.catalog.findings),
            "inference": len(self.catalog.inferences),
        }
        total = sum(goals.values())
        complete = sum(counts.values())
        stage = self.catalog.rules["secondRound"]["requirements"]
        enough_inference = len(state["derivedEvidence"]) >= stage["inference"]
        enough_findings = len(state["contradictions"]) >= stage["findings"]
        eligible = enough_inference and enough_findings
        active = not state["verdict"]

        safe["progress"] = {
            "counts": counts,
            "goals": goals,
            "completed": complete,
            "total": total,
            "percent": min(100, math.floor(complete / total * 100 + 0.5)),
        }
        safe["timeline"] = self.timeline(state)
        safe["materials"] = self.materials(state)
        safe["accusationReadiness"] = self.engine.readiness(state)
        safe["secondRoundEligibility"] = {
            "inference": len(state["derivedEvidence"]),
            "findings": len(state["contradictions"]),
            "eligible": eligible,
        }
        safe["availableActions"] = {
            "interrogate": active
            and state["questions"] < self.catalog.rules["questionLimit"],
            "advance": active and state["phase"] == 1 and eligible,
            "accuse": active,
            "notes": active,
        }
        safe["remainingQuestions"] = max(
            0, self.catalog.rules["questionLimit"] - state["questions"]
        )

        # 실제 획득한 자료만 추론 선택 목록에 넣는다.
        references = []
        for evidence_id, evidence in self.catalog.evidence.items():
            if evidence_id not in state["examined"]:
                continue
            if evidence["phase"] <= state["phase"]:
                references.append({"kind": "evidence", "id": evidence_id})
        for statement_id in state["statements"]:
            references.append({"kind": "testimony", "id": statement_id})
        for document_id in state["derivedEvidence"]:
            references.append({"kind": "derived", "id": document_id})
        safe["inferenceSources"] = []
        for reference in references:
            safe["inferenceSources"].append(self.describe_source(state, reference))

        physical_count = 0
        physical_read_count = 0
        for material in safe["materials"]:
            if material["kind"] == "evidence" and material["archiveKind"] == "evidence":
                physical_count += 1
                if material["acquired"]:
                    physical_read_count += 1

        labels = {}
        for document in state["derivedEvidence"].values():
            categories = set()
            source_keys = []
            for reference in document["leafSources"]:
                description = self.describe_source(state, reference)
                categories.add(description["category"])
                source_keys.append(reference["kind"] + ":" + reference["id"])
            source_keys.sort()
            key = "|".join(source_keys)
            if "evidence" in categories and "testimony" in categories:
                labels[key] = "증거·증언 교차 추론"
            elif "testimony" in categories:
                labels[key] = "증언 비교 추론"
            else:
                labels[key] = "증거 비교 추론"
        required_ids = []
        for document_id in self.catalog.rules["accusation"]["requiredInferenceIds"]:
            if document_id in state["derivedEvidence"]:
                required_ids.append(document_id)
        safe["ui"] = {
            "requiredInferenceIds": required_ids,
            "basisLabels": labels,
            "physicalCount": physical_count,
            "physicalReadCount": physical_read_count,
        }
        if safe["verdict"]:
            safe["verdict"]["checkDetails"] = deepcopy(RESULT_CHECK_DETAILS)
        return safe
