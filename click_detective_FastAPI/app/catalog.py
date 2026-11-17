"""복사된 데이터의 무결성을 확인하고 정적 사건·비공개 규칙을 서버에서만 읽는다."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from fastapi import HTTPException


class Catalog:
    """런타임은 Next.js나 TypeScript를 실행하지 않는다. 모든 데이터는 자체 data에서 읽는다."""

    def __init__(self, root: Path):
        """시작 시 파일 해시를 확인한다. 원본 프로젝트나 개인 플레이 기록은 읽지 않는다."""
        self.root = root.resolve()
        manifest_bytes = (root / "manifest.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        for item in manifest["files"]:
            path = (root / item["path"]).resolve()
            if not path.is_relative_to(self.root) or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                raise ValueError("Copied data integrity mismatch")
        self.version = "snapshot-" + hashlib.sha256(manifest_bytes).hexdigest()[:16]
        self.case = self.read("case.json")
        self.case_id = self.case["caseId"]
        self.people = {person["id"]: person for person in self.read("characters.json")["characters"]}
        self.evidence = {record["id"]: record for record in self.read("evidence.json")["records"]}
        self.findings = self.read("findings.private.json")["rules"]
        self.inferences = self.read("inferences.private.json")["rules"]
        self.testimony = self.read("testimony-templates.private.json")
        self.rules = self.read("game-rules.json")
        self.solution = self.read("solution.private.json")
        self.scripts = self.read("character-scripts.private.json")
        self.statement_people = {item["suspectId"]: item for item in self.testimony["characters"]}

    def read(self, name: str):
        """서버 코드가 지정한 정적 파일만 읽는다. 클라이언트 경로를 전달하지 않는다."""
        return json.loads((self.root / "case" / name).read_text(encoding="utf-8"))

    def require_case(self, case_id):
        """실제 실행 가능한 사건을 검사한다. 예정 사건을 수사로 시작하지 않는다."""
        if case_id != self.case_id:
            raise HTTPException(404, "사건을 찾을 수 없습니다.")

    def public_catalog(self):
        """초기 화면 콘텐츠·인물·선택지만 명시적으로 공개한다. 규칙 원문은 제외한다."""
        people = []
        for person in self.people.values():
            safe = {key: deepcopy(person[key]) for key in (
                "id", "name", "en", "age", "role", "initials", "color", "statement", "bio", "suggestions", "interviewTopics")}
            safe["portrait"] = "/v1/assets/" + person["portrait"].lstrip("/")
            people.append(safe)
        presentation = self.read("story-presentation.json")
        blocks = presentation.get("briefing", {}).get("blocks", [])
        return {"caseId": self.case_id, "scenarioVersion": self.version, "case": deepcopy(self.case["case"]),
                "motiveOptions": deepcopy(self.case["motiveOptions"]), "methodOptions": deepcopy(self.case["methodOptions"]),
                "publicTimeline": deepcopy(self.case["publicTimeline"]), "characters": people,
                "questionLimit": self.rules["questionLimit"],
                "briefing": [{"tag": block["tag"], "text": block["text"]} for block in blocks if "{" not in block["text"]],
                "openingVideo": "/v1/assets/assets/intro/thirteenth-bell-opening-v3-quiet.mp4",
                "application": self.read("application-data.json"),
                "display": {
                    "evidence": [{**{key: deepcopy(record[key]) for key in
                        ("id", "code", "type", "title", "time", "phase", "summary")},
                        "body": "", "archiveKind": record.get("archiveKind", "evidence")}
                        for record in self.evidence.values()],
                    "revelationCount": len(self.findings),
                    "secondRoundRequirements": deepcopy(self.rules["secondRound"]["requirements"]),
                    "accusationMinimum": 0,
                },
                "screenLabels": {"evidence": "증거 보관실", "testimony": "증언 기록", "findings": "발견한 쟁점", "inference": "추론 증거"}}

    def public_asset(self, path: str):
        """증거·비공개 JSON은 공개 정적 자산 경로로 제공하지 않는다."""
        candidate = (self.root / "public" / path).resolve()
        if (not candidate.is_relative_to(self.root / "public") or path.startswith("assets/evidence/")
                or candidate.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".svg", ".mp3"}
                or not candidate.is_file()):
            raise HTTPException(404, "자산을 찾을 수 없습니다.")
        return candidate
