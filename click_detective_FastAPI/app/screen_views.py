"""원본 Next.js 자료실의 검색·분류 결과를 FastAPI에서 구성하는 표시 전용 서비스."""


class ScreenViews:
    """게임 규칙을 바꾸지 않고 같은 상태를 원본 화면이 요구하는 목록으로 변환한다."""

    def __init__(self, catalog, presenter):
        """사건 원본과 공개 상태 변환기를 받아 중복된 프런트엔드 데이터 처리를 없앤다."""
        self.c, self.presenter = catalog, presenter

    def evidence(self, state, search="", place="all"):
        """물증·문서를 장소별로 분류한다. 검색은 원본의 공백·대소문자 동작을 유지한다."""
        available = [item for item in self.presenter.materials(state)
                     if item["kind"] == "evidence" and item["archiveKind"] == "evidence"]
        places = list(dict.fromkeys(item["type"] for item in available))
        query = search.strip().lower()
        groups = []
        for name in places:
            records = [item for item in available if item["type"] == name and
                       query in " ".join(item[key] for key in ("code", "title", "type", "summary")).lower()]
            if records and place in {"all", name}:
                groups.append({"name": name, "records": records})
        return {"available": available, "places": places, "groups": groups,
                "readCount": sum(item["acquired"] for item in available)}

    def testimonies(self, state, search="", person="all"):
        """최초 진술·집사 문서·획득 증언·질문/답변 쌍을 원본 화면과 같은 순서로 검색한다."""
        query = search.strip().lower()
        witnesses = [{"id": "butler", "name": "집사 노씨"}] + list(self.c.people.values())
        result = []
        for witness in witnesses:
            key, name = witness["id"], witness["name"]
            if person not in {"all", key}:
                continue
            messages = [{**item, "index": index} for index, item in enumerate(state["messages"])
                        if item["suspectId"] == key]
            by_index = {item["index"]: item for item in messages}
            pairs = []
            for question in messages:
                if question["role"] != "user":
                    continue
                answer = by_index.get(question["index"] + 1)
                if answer and answer["role"] != "suspect":
                    answer = None
                material = state["derivedEvidence"].get(question.get("evidenceId"),
                            self.c.evidence.get(question.get("evidenceId"), {}))
                text = " ".join([name, question["text"], (answer or {}).get("text", ""),
                                 question.get("evidenceId") or "", material.get("title", "")])
                if query in text.lower():
                    pairs.append({"question": question, "answer": answer})
            initial = witness.get("statement")
            if not initial or query not in (name + " " + initial).lower():
                initial = None
            records = []
            if key == "butler":
                records = [{**{field: record[field] for field in
                            ("id", "code", "title", "summary", "phase", "type", "time")}}
                           for record in self.c.evidence.values()
                           if record.get("archiveKind") == "testimony" and record["phase"] <= state["phase"]
                           and query in (name + " " + record["code"] + " " + record["title"] + " " + record["body"]).lower()]
            acquired = [item for item in state["statements"].values() if item["speaker"] == key
                        and query in (name + " " + item["code"] + " " + item["title"] + " " + item["excerpt"]).lower()]
            if initial or pairs or records or acquired:
                result.append({"id": key, "name": name, "initial": initial, "pairs": pairs,
                               "records": records, "acquired": acquired})
        return {"visible": result}

    def inference(self, state, search="", category="evidence"):
        """획득한 실제 출처를 자료 종류와 검색어로 골라 원본 추론 선택창에 제공한다."""
        sources = self.presenter.state(state)["inferenceSources"]
        query = search.strip().lower()
        return {"visible": [item for item in sources if item["category"] == category and
                query in (item["code"] + " " + item["title"] + " " + item["context"]).lower()]}
