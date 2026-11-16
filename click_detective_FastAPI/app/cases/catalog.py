"""복사된 데이터의 무결성을 확인하고 정적 사건·비공개 규칙을 서버에서만 읽는다."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from fastapi import HTTPException


class Catalog:
    """런타임은 Next.js나 TypeScript를 실행하지 않는다. 모든 데이터는 자체 data에서 읽는다.

    Args:
        root (Path): 정적 사건 데이터가 있는 최상위 디렉터리.

    Returns:
        Catalog: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, root: Path):
        """시작 시 파일 해시를 확인한다. 원본 프로젝트나 개인 플레이 기록은 읽지 않는다.

        Args:
            root (Path): 정적 사건 데이터가 있는 최상위 디렉터리.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.root = root.resolve()
        manifest_bytes = (root / "manifest.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        for item in manifest["files"]:
            path = (root / item["path"]).resolve()
            if not path.is_relative_to(self.root):
                raise ValueError("Copied data integrity mismatch")
            file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if file_hash != item["sha256"]:
                raise ValueError("Copied data integrity mismatch")
        self.version = "snapshot-" + hashlib.sha256(manifest_bytes).hexdigest()[:16]
        self.case = self.read("case.json")
        self.case_id = self.case["caseId"]
        self.people = {}
        characters = self.read("characters.json")["characters"]
        for person in characters:
            self.people[person["id"]] = person

        self.evidence = {}
        records = self.read("evidence.json")["records"]
        for record in records:
            self.evidence[record["id"]] = record
        self.findings = self.read("findings.private.json")["rules"]
        self.inferences = self.read("inferences.private.json")["rules"]
        self.testimony = self.read("testimony-templates.private.json")
        self.rules = self.read("game-rules.json")
        self.solution = self.read("solution.private.json")
        self.scripts = self.read("character-scripts.private.json")
        self.statement_people = {}
        for person in self.testimony["characters"]:
            self.statement_people[person["suspectId"]] = person

    def read(self, name: str):
        """서버 코드가 지정한 정적 파일만 읽는다. 클라이언트 경로를 전달하지 않는다.

        Args:
            name (str): 읽을 파일 또는 실행할 사례의 이름.

        Returns:
            dict: 지정한 사건 JSON 파일에서 읽은 데이터.
        """
        return json.loads((self.root / "case" / name).read_text(encoding="utf-8"))

    def require_case(self, case_id):
        """실제 실행 가능한 사건을 검사한다. 예정 사건을 수사로 시작하지 않는다.

        Args:
            case_id: 조회하거나 생성할 사건의 식별자.

        Returns:
            None: 반환값 없음.
        """
        if case_id != self.case_id:
            raise HTTPException(404, "사건을 찾을 수 없습니다.")

    def public_catalog(self):
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
        for person in self.people.values():
            public_person = {}
            for field in person_fields:
                public_person[field] = deepcopy(person[field])
            public_person["portrait"] = "/v1/assets/" + person["portrait"].lstrip("/")
            people.append(public_person)

        # 증거 목록에는 제목과 요약만 넣고, 아직 본문을 공개하지 않는다.
        evidence = []
        evidence_fields = ["id", "code", "type", "title", "time", "phase", "summary"]
        for record in self.evidence.values():
            public_record = {}
            for field in evidence_fields:
                public_record[field] = deepcopy(record[field])
            public_record["body"] = ""
            public_record["archiveKind"] = record.get("archiveKind", "evidence")
            evidence.append(public_record)

        presentation = self.read("story-presentation.json")
        blocks = presentation.get("briefing", {}).get("blocks", [])
        briefing = []
        for block in blocks:
            if "{" in block["text"]:
                continue
            briefing.append({"tag": block["tag"], "text": block["text"]})

        display = {
            "evidence": evidence,
            "revelationCount": len(self.findings),
            "secondRoundRequirements": deepcopy(
                self.rules["secondRound"]["requirements"]
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
            "caseId": self.case_id,
            "scenarioVersion": self.version,
            "case": deepcopy(self.case["case"]),
            "motiveOptions": deepcopy(self.case["motiveOptions"]),
            "methodOptions": deepcopy(self.case["methodOptions"]),
            "publicTimeline": deepcopy(self.case["publicTimeline"]),
            "characters": people,
            "questionLimit": self.rules["questionLimit"],
            "briefing": briefing,
            "openingVideo": "/v1/assets/assets/intro/thirteenth-bell-opening-v3-quiet.mp4",
            "application": self.read("application-data.json"),
            "display": display,
            "screenLabels": screen_labels,
        }

    def public_asset(self, path: str):
        """증거·비공개 JSON은 공개 정적 자산 경로로 제공하지 않는다.

        Args:
            path (str): 저장 파일 경로나 HTTP 요청 경로.

        Returns:
            Path: 공개 자산의 검증된 실제 파일 경로.
        """
        candidate = (self.root / "public" / path).resolve()
        if (
            not candidate.is_relative_to(self.root / "public")
            or path.startswith("assets/evidence/")
            or candidate.suffix.lower()
            not in {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".svg"}
            or not candidate.is_file()
        ):
            raise HTTPException(404, "자산을 찾을 수 없습니다.")
        return candidate
