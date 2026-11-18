"""고발의 근거 충족 여부와 점수를 계산한다."""

from copy import deepcopy

from fastapi import HTTPException


class AccusationRules:
    """제출한 추론 근거와 고발 선택을 평가한다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

    Returns:
        AccusationRules: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, catalog):
        """사용할 의존성과 초기 상태를 준비한다.

        Args:
            catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.catalog = catalog

    def covered(self, state, ids):
        """제출한 실제 추론의 원본 근거 중 실제 열람한 자료만 계산한다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            ids: 실제 획득하여 제출한 추론 증거 식별자 목록.

        Returns:
            set[str]: 제출한 추론이 뒷받침하는 실제 열람 원본 증거 ID.
        """
        result = set()
        for key in ids:
            for ref in state["derivedEvidence"][key]["leafSources"]:
                if ref["kind"] == "evidence" and ref["id"] in state["examined"]:
                    result.add(ref["id"])
        return result

    def accuse(self, state, command):
        """언제든 고발을 받아 채점한다. 부족한 입증은 제출 차단 대신 점수에 반영한다.

        조사 단계·발견 쟁점 수·추론 개수는 제출 조건이 아니다. 제출한 ID가 있다면
        실제 확보한 서로 다른 추론인지 검사하고, 핵심 근거 충족 여부로 채점한다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

        Returns:
            dict: 정답 일치, 점수, 제출 근거 평가와 사건 해설.
        """
        if (
            command.suspect_id not in self.catalog.people
            or command.motive
            not in {x["id"] for x in self.catalog.case["motiveOptions"]}
            or command.method
            not in {x["id"] for x in self.catalog.case["methodOptions"]}
        ):
            raise HTTPException(422, "모든 고발 항목을 확인하세요.")
        ids = command.evidence_ids
        if len(set(ids)) != len(ids) or any(
            key not in state["derivedEvidence"] for key in ids
        ):
            raise HTTPException(422, "확보한 서로 다른 추론 증거를 제출하세요.")
        covered = self.covered(state, ids)
        rules = self.catalog.rules["accusation"]
        core = all(key in ids for key in rules["requiredInferenceIds"]) and all(
            set(group) & covered for group in rules["coreEvidenceGroups"]
        )
        answer = self.catalog.solution["solution"]
        flags = [
            command.suspect_id == answer["suspectId"],
            command.motive == answer["motive"],
            command.method == answer["method"],
            bool(core),
        ]
        review = {
            "findings": [
                {
                    "id": rule["flag"],
                    "title": rule["label"],
                    "discovered": rule["flag"] in state["revealed"],
                }
                for rule in self.catalog.findings
            ],
            "inference": [
                {
                    "id": "derived-" + rule["id"],
                    "title": rule["title"],
                    "discovered": "derived-" + rule["id"] in state["derivedEvidence"],
                    "submitted": "derived-" + rule["id"] in ids,
                }
                for rule in self.catalog.inferences
            ],
        }
        submitted = []
        for key in ids:
            own = self.covered(state, [key])
            contribution = []
            for group in rules["coreEvidenceGroups"]:
                for item in group:
                    if item in own:
                        contribution.append(item)
            submitted.append(
                {
                    "id": key,
                    "title": state["derivedEvidence"][key]["title"],
                    "kind": "derived",
                    "contributes": bool(contribution),
                    "coveredTitles": [
                        self.catalog.evidence[item]["title"] for item in contribution
                    ],
                }
            )
        missing = []
        for group in rules["coreEvidenceGroups"]:
            if not set(group) & covered:
                missing.append(
                    {
                        "id": "|".join(group),
                        "title": " 또는 ".join(
                            (self.catalog.evidence[item]["title"] for item in group)
                        ),
                    }
                )
        missing += [
            {
                "id": key,
                "title": "필수 추론: "
                + state["derivedEvidence"].get(key, {}).get("title", key),
            }
            for key in rules["requiredInferenceIds"]
            if key not in ids
        ]
        state["verdict"] = {
            "correct": all(flags),
            "score": sum(flags) * self.catalog.solution["pointsPerCheck"],
            "checks": [
                {"label": label, "correct": value}
                for label, value in zip(self.catalog.solution["checks"], flags)
            ],
            "submittedEvidenceIds": ids,
            "evidenceAssessment": {"submitted": submitted, "missing": missing},
            "review": review,
            "explanation": self.catalog.solution["explanation"],
        }
        return deepcopy(state["verdict"])
