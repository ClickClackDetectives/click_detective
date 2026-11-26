"""사건 조회와 공개 카탈로그 조립을 담당한다."""

from copy import deepcopy
from pathlib import Path

from ..dto.cases_catalog_dto import PublicCatalog
from ..repositories.cases_file_repository import Catalog


class CatalogService:
    """사건 저장소의 데이터로 공개 API 응답을 조립한다.

    Args:
        repository: 기동 시 무결성을 확인한 사건 파일 저장소.

    Returns:
        CatalogService: 공개 사건 목록과 카탈로그를 제공하는 서비스.
    """

    def __init__(self, repository: Catalog):
        """공개 응답을 조립할 사건 파일 저장소를 보관한다.

        Args:
            repository: 기동 시 무결성을 확인한 사건 파일 저장소.

        Returns:
            None: 반환값 없음.
        """
        self.repository = repository

    def list_cases(self) -> dict:
        """현재 시작할 수 있는 사건의 소개와 버전을 반환한다.

        Args:
            없음.

        Returns:
            dict: 시작 가능한 사건을 cases 목록에 담은 응답.
        """
        data = self.repository
        return {
            "cases": [
                {
                    "case_id": data.case_id,
                    "scenario_version": data.version,
                    **data.case["case"],
                }
            ]
        }

    def case_detail(self, case_id: str) -> PublicCatalog:
        """사건 ID를 확인하고 해당 사건의 공개 카탈로그를 반환한다.

        Args:
            case_id: 조회할 사건의 식별자.

        Returns:
            PublicCatalog: 사건 소개와 화면에 공개되는 정보.

        Raises:
            HTTPException: 현재 시작 가능한 사건의 ID와 다르면 404가 발생한다.
        """
        self.repository.require_case(case_id)
        return self.public_catalog()

    def public_asset(self, asset_path: str) -> Path:
        """공개 자산 요청에 사용할 파일 경로를 반환한다.

        Args:
            asset_path: 공개 디렉터리 기준 상대 경로.

        Returns:
            Path: 공개 여부와 존재를 확인한 실제 파일 경로.

        Raises:
            HTTPException: 공개 대상이 아니거나 파일이 없으면 404가 발생한다.
        """
        return self.repository.public_asset(asset_path)

    def public_catalog(self) -> PublicCatalog:
        """초기 화면 콘텐츠·인물·선택지만 명시적으로 공개한다. 규칙 원문은 제외한다.

        Args:
            없음.

        Returns:
            dict: 공개가 허용된 사건·인물·자료 목록과 화면 설정.
        """
        # 인물 정보에서 화면에 공개할 항목만 복사한다.
        people = []
        person_fields = [
            "id",
            "name",
            "en",
            "age",
            "role",
            "initials",
            "color",
            "statement",
            "bio",
            "suggestions",
            "interviewTopics",
        ]
        for person in self.repository.people.values():
            public_person = {}
            for field in person_fields:
                public_person[field] = deepcopy(person[field])
            public_person["portrait"] = "/v1/assets/" + person["portrait"].lstrip("/")
            people.append(public_person)

        # 증거 목록에는 제목과 요약만 넣고, 아직 본문을 공개하지 않는다.
        evidence = []
        evidence_fields = ["id", "code", "type", "title", "time", "phase", "summary"]
        for record in self.repository.evidence.values():
            public_record = {}
            for field in evidence_fields:
                public_record[field] = deepcopy(record[field])
            public_record["body"] = ""
            public_record["archiveKind"] = record.get("archiveKind", "evidence")
            evidence.append(public_record)

        presentation = self.repository.read("story-presentation.json")
        blocks = presentation.get("briefing", {}).get("blocks", [])
        briefing = []
        for block in blocks:
            if "{" in block["text"]:
                continue
            briefing.append({"tag": block["tag"], "text": block["text"]})

        display = {
            "evidence": evidence,
            "revelationCount": len(self.repository.findings),
            "secondRoundRequirements": deepcopy(
                self.repository.rules["secondRound"]["requirements"]
            ),
            "accusationMinimum": 0,
        }
        screen_labels = {
            "evidence": "증거 보관실",
            "testimony": "증언 기록",
            "findings": "발견한 쟁점",
            "inference": "추론 증거",
        }
        return {
            "caseId": self.repository.case_id,
            "scenarioVersion": self.repository.version,
            "case": deepcopy(self.repository.case["case"]),
            "motiveOptions": deepcopy(self.repository.case["motiveOptions"]),
            "methodOptions": deepcopy(self.repository.case["methodOptions"]),
            "publicTimeline": deepcopy(self.repository.case["publicTimeline"]),
            "characters": people,
            "questionLimit": self.repository.rules["questionLimit"],
            "briefing": briefing,
            "openingVideo": "/v1/assets/assets/intro/thirteenth-bell-opening-v3-quiet.mp4",
            "application": self.repository.read("application-data.json"),
            "display": display,
            "screenLabels": screen_labels,
        }
