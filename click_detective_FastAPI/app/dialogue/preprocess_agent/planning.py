"""게임 규칙으로 공개 가능한 심문 진술과 쟁점을 준비한다."""

import re
from copy import deepcopy
from dataclasses import dataclass

from fastapi import HTTPException

from .approval_materials import collect_findings, collect_materials
from .free_questions import free_entries, movement


def facts_from_entries(suspect_id, entries):
    """수사 기록용 진술을 생성에 쓸 승인 사실로 변환한다.

    Args:
        suspect_id: 진술을 한 인물의 식별자.
        entries: 현재 공개 상태에서 선택된 원문 진술.
    Returns:
        list[dict]: 생성과 검증에 사용하는 승인 사실.
    """
    return [
        {
            "id": f"{suspect_id}-{entry['key']}",
            "text": entry["text"],
            "nature": entry["nature"].replace("추측·인상", "추측/인상"),
        }
        for entry in entries
    ]


@dataclass
class ReplyPlan:
    """생성할 사실과 확정할 구조화 기록을 분리한 요청별 계획.

    Args:
        suspect_id (str): 심문 대상 인물의 식별자.
        question (str): 사용자가 입력한 질문 원문.
        topic (str | None): 질문에서 명시할 주제 식별자.
        entries (list[dict]): 게임 기록에 반영할 승인 진술.
        facts (list[dict]): 모델에 제공할 승인 사실.
        new_findings (list[dict]): 이번 심문으로 새로 공개할 쟁점.
        sources (list[dict]): 진술과 쟁점의 실제 근거.
        material_id (str | None): 이번 심문에 제시한 자료 식별자.

    Returns:
        ReplyPlan: 위 역할을 수행하도록 생성된 객체.
    """

    suspect_id: str
    question: str
    topic: str | None
    entries: list[dict]
    facts: list[dict]
    new_findings: list[dict]
    sources: list[dict]
    material_id: str | None


class Planner:
    """자료 획득·인물별 누적 제시·인정 상태로 이번에 말할 사실만 고른다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

    Returns:
        Planner: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, catalog):
        """현재 사건의 서버 전용 템플릿을 사용한다.

        Args:
            catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.catalog = catalog

    def movement(self, suspect, flags):
        """인정 플래그 조합에 맞는 동선 원문만 선택한다. 후보 전체를 모델에 주지 않는다.

        Args:
            suspect: 심문 대상 인물의 식별자.
            flags: 현재까지 인정되거나 공개된 쟁점 식별자 목록.

        Returns:
            list[dict]: 현재 인정 상태에 맞는 동선 진술.
        """
        return movement(self.catalog, suspect, flags)

    def resolve_topic(self, suspect, question, explicit):
        """명시적 주제는 허용 목록으로 검사하고 자유 입력은 알려진 주제만 추정한다.

        Args:
            suspect: 심문 대상 인물의 식별자.
            question: 사용자가 입력한 질문 원문.
            explicit: 사용자가 명시한 질문 주제. 없으면 질문에서 추정한다.

        Returns:
            str | None: 허용된 질문 주제. 추정할 수 없으면 None.
        """
        topics = []
        for topic in self.catalog.people[suspect]["interviewTopics"]:
            topics.append(topic["id"])
        if explicit:
            if explicit not in topics:
                raise HTTPException(422, "질문 주제를 확인하세요.")
            return explicit
        for person in self.catalog.people.values():
            if (
                person["id"] != suspect
                and person["name"] in question
                and re.search(r"대해|알고|보았|봤|관계", question)
            ):
                return "about-" + person["id"]
        if re.search(r"동선|행적|그날 밤.*행동", question):
            return "movement"
        return None

    def expand_material(self, state, material_id):
        """열람한 원본 또는 실제 생성한 추론만 제시하도록 허용한다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            material_id: 이번 심문에 제시한 자료 식별자.

        Returns:
            list[dict]: 제시 자료를 구성하는 실제 원본 출처.
        """
        if material_id in state["derivedEvidence"]:
            return state["derivedEvidence"][material_id]["leafSources"]
        record = self.catalog.evidence.get(material_id)
        if (
            record is None
            or record["phase"] > state["phase"]
            or material_id not in state["examined"]
        ):
            raise HTTPException(422, "먼저 해당 자료를 열람하세요.")
        return [{"kind": "evidence", "id": material_id}]

    def prepare(self, state, command, *, search_free=False):
        """질문·자료를 검사하고 원래 상태를 바꾸지 않은 채 승인 계획을 반환한다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
            search_free: 자유 질문의 진술 선택을 벡터 검색에 맡길지 여부.

        Returns:
            ReplyPlan: 공개할 사실과 저장할 진술·쟁점 정보. 입력 상태는 확정 변경하지 않는다.
        """
        suspect = command.suspect_id
        if suspect not in self.catalog.people:
            raise HTTPException(422, "인물을 확인하세요.")
        if state["questions"] >= self.catalog.rules["questionLimit"]:
            raise HTTPException(429, "심문 한도를 모두 사용했습니다.")
        topic = None
        if command.topic_id or not search_free:
            topic = self.resolve_topic(suspect, command.question, command.topic_id)
        physical_ids, sources = collect_materials(self, state, command)
        findings = collect_findings(self.catalog, state, command, physical_ids)
        flags = list(state["revealed"])
        for rule in findings:
            flags.append(rule["flag"])
        entries = []
        facts = []
        if findings:
            replies = {}
            for item in self.catalog.testimony["admissionReplies"]:
                replies[item["flag"]] = item["reply"]
            for rule in findings:
                entry = self.catalog.testimony["admissionEntries"].get(rule["flag"])
                if entry:
                    entries.append(deepcopy(entry))
                    fact_key = entry["key"]
                    nature = entry["nature"]
                else:
                    fact_key = "finding-" + rule["flag"]
                    nature = "추측/인상"
                facts.append(
                    {
                        "id": suspect + "-" + fact_key,
                        "text": replies[rule["flag"]],
                        "nature": nature,
                    }
                )
        elif topic == "movement":
            entries = self.movement(suspect, flags)
        elif topic and topic.startswith("about-"):
            relationship_replies = self.catalog.statement_people[suspect][
                "relationshipReplies"
            ]
            for reply in relationship_replies:
                if reply["topicId"] == topic:
                    entries = deepcopy(reply["entries"])
                    break
            else:
                raise StopIteration
        elif not search_free:
            entries = self.free_entries(suspect, command.question, flags)
        if not facts:
            facts = facts_from_entries(suspect, entries)
        return ReplyPlan(
            suspect,
            command.question,
            topic,
            entries,
            facts,
            deepcopy(findings),
            sources,
            command.material_id,
        )

    def free_entries(self, suspect, question, flags):
        """자유 질문을 공개 동선·관계·이미 인정한 진술에 연결한다. 미승인 비밀은 선택하지 않는다.

        Args:
            suspect: 심문 대상 인물의 식별자.
            question: 사용자가 입력한 질문 원문.
            flags: 현재까지 인정되거나 공개된 쟁점 식별자 목록.

        Returns:
            list[dict]: 질문과 관련하여 공개 가능한 진술. 없으면 빈 목록.
        """
        return free_entries(self.catalog, suspect, question, flags)
