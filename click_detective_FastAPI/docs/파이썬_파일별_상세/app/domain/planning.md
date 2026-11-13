# app/domain/planning.py 상세 설명

[문서 목차](../../../README.md) · [파일별 목차](../../README.md) · [현재 소스](../../../../app/domain/planning.py)

## 역할과 읽는 순서

심문 승인 계획. LLM은 공개 사실·쟁점·기록 ID를 결정하지 않는다.

LLM보다 먼저 공개할 사실과 새 쟁점을 결정합니다. 같은 인물에게 제시한 자료를 누적하며 단순 열람을 제시로 취급하지 않습니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## ReplyPlan

[원본 10번째 줄](../../../../app/domain/planning.py#L10)

생성할 사실과 확정할 구조화 기록을 분리한 요청별 계획.

### 선언 필드

```python
suspect_id: str
question: str
topic: str | None
entries: list[dict]
facts: list[dict]
new_findings: list[dict]
sources: list[dict]
material_id: str | None
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Planner

[원본 22번째 줄](../../../../app/domain/planning.py#L22)

자료 획득·인물별 누적 제시·인정 상태로 이번에 말할 사실만 고른다.

## Planner.__init__

[원본 25번째 줄](../../../../app/domain/planning.py#L25)

현재 사건의 서버 전용 템플릿을 사용한다.

### 입력과 처리

```python
def __init__(self, catalog):
```

### 실제 코드

````python
def __init__(self, catalog):
        """현재 사건의 서버 전용 템플릿을 사용한다."""
        self.catalog = catalog
````

## Planner.movement

[원본 29번째 줄](../../../../app/domain/planning.py#L29)

인정 플래그 조합에 맞는 동선 원문만 선택한다. 후보 전체를 모델에 주지 않는다.

### 입력과 처리

```python
def movement(self, suspect, flags):
```

### 실제 코드

````python
def movement(self, suspect, flags):
        """인정 플래그 조합에 맞는 동선 원문만 선택한다. 후보 전체를 모델에 주지 않는다."""
        variants = self.catalog.statement_people[suspect]["movementVariants"]
        relevant = {flag for variant in variants for flag in variant["recognizedFlags"]}
        selected = set(flags) & relevant
        return deepcopy(next(variant["entries"] for variant in variants if set(variant["recognizedFlags"]) == selected))
````

## Planner.resolve_topic

[원본 36번째 줄](../../../../app/domain/planning.py#L36)

명시적 주제는 허용 목록으로 검사하고 자유 입력은 알려진 주제만 추정한다.

### 입력과 처리

```python
def resolve_topic(self, suspect, question, explicit):
```

주요 분기 조건은 `explicit`, `explicit not in topics`, `person['id'] != suspect and person['name'] in question and re.search('대해|알고|보았|봤|관계', question)`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def resolve_topic(self, suspect, question, explicit):
        """명시적 주제는 허용 목록으로 검사하고 자유 입력은 알려진 주제만 추정한다."""
        topics = {topic["id"] for topic in self.catalog.people[suspect]["interviewTopics"]}
        if explicit:
            if explicit not in topics:
                raise HTTPException(422, "질문 주제를 확인하세요.")
            return explicit
        for person in self.catalog.people.values():
            if person["id"] != suspect and person["name"] in question and re.search(r"대해|알고|보았|봤|관계", question):
                return "about-" + person["id"]
        return "movement" if re.search(r"동선|행적|그날 밤.*행동", question) else None
````

## Planner.expand_material

[원본 48번째 줄](../../../../app/domain/planning.py#L48)

열람한 원본 또는 실제 생성한 추론만 제시하도록 허용한다.

### 입력과 처리

```python
def expand_material(self, state, material_id):
```

주요 분기 조건은 `material_id in state['derivedEvidence']`, `record is None or record['phase'] > state['phase'] or material_id not in state['examined']`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def expand_material(self, state, material_id):
        """열람한 원본 또는 실제 생성한 추론만 제시하도록 허용한다."""
        if material_id in state["derivedEvidence"]:
            return state["derivedEvidence"][material_id]["leafSources"]
        record = self.catalog.evidence.get(material_id)
        if record is None or record["phase"] > state["phase"] or material_id not in state["examined"]:
            raise HTTPException(422, "먼저 해당 자료를 열람하세요.")
        return [{"kind": "evidence", "id": material_id}]
````

## Planner.prepare

[원본 57번째 줄](../../../../app/domain/planning.py#L57)

질문·자료를 검사하고 원래 상태를 바꾸지 않은 채 승인 계획을 반환한다.

### 입력과 처리

```python
def prepare(self, state, command):
```

주요 분기 조건은 `suspect not in self.catalog.people`, `state['questions'] >= self.catalog.rules['questionLimit']`, `findings`, `not facts`, `topic == 'movement'`, `entry` 등입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def prepare(self, state, command):
        """질문·자료를 검사하고 원래 상태를 바꾸지 않은 채 승인 계획을 반환한다."""
        suspect = command.suspect_id
        if suspect not in self.catalog.people:
            raise HTTPException(422, "인물을 확인하세요.")
        if state["questions"] >= self.catalog.rules["questionLimit"]:
            raise HTTPException(429, "심문 한도를 모두 사용했습니다.")
        topic = self.resolve_topic(suspect, command.question, command.topic_id)
        material_ids = list(dict.fromkeys([message["evidenceId"] for message in state["messages"]
            if message["suspectId"] == suspect and message.get("evidenceId")] + ([command.material_id] if command.material_id else [])))
        physical = {ref["id"] for material_id in material_ids for ref in self.expand_material(state, material_id) if ref["kind"] == "evidence"}
        sources = [{"kind": "derived" if value in state["derivedEvidence"] else "evidence", "id": value} for value in material_ids]
        findings = [rule for rule in self.catalog.findings if command.material_id and rule["suspectId"] == suspect
                    and rule["flag"] not in state["revealed"] and set(rule["need"]).issubset(physical)]
        flags = state["revealed"] + [rule["flag"] for rule in findings]
        entries = []
        facts = []
        if findings:
            replies = {item["flag"]: item["reply"] for item in self.catalog.testimony["admissionReplies"]}
            for rule in findings:
                entry = self.catalog.testimony["admissionEntries"].get(rule["flag"])
                if entry:
                    entries.append(deepcopy(entry))
                facts.append({"id": suspect + "-" + (entry["key"] if entry else "finding-" + rule["flag"]),
                              "text": replies[rule["flag"]], "nature": entry["nature"] if entry else "추측/인상"})
        elif topic == "movement":
            entries = self.movement(suspect, flags)
        elif topic and topic.startswith("about-"):
            entries = deepcopy(next(item["entries"] for item in self.catalog.statement_people[suspect]["relationshipReplies"] if item["topicId"] == topic))
        else:
            entries = self.free_entries(suspect, command.question, flags)
        if not facts:
            facts = [{"id": suspect + "-" + entry["key"], "text": entry["text"], "nature": entry["nature"].replace("추측·인상", "추측/인상")} for entry in entries]
        return ReplyPlan(suspect, command.question, topic, entries, facts, deepcopy(findings), sources, command.material_id)
````

## Planner.free_entries

[원본 92번째 줄](../../../../app/domain/planning.py#L92)

자유 질문을 공개 동선·관계·이미 인정한 진술에 연결한다. 미승인 비밀은 선택하지 않는다.

### 입력과 처리

```python
def free_entries(self, suspect, question, flags):
```

주요 분기 조건은 `re.search('대학|학력|레시피|프롬프트|지침|역할.*바꿔|정답.*알려', question)`, `re.search('누구|직업|몇.*살|나이|자기소개', question)`, `flag in flags and flag in own_flags and re.search(pattern, question) and (flag in admissions)`, `match and re.search(pattern, question)`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def free_entries(self, suspect, question, flags):
        """자유 질문을 공개 동선·관계·이미 인정한 진술에 연결한다. 미승인 비밀은 선택하지 않는다."""
        if re.search(r"대학|학력|레시피|프롬프트|지침|역할.*바꿔|정답.*알려", question):
            return []
        movement = self.movement(suspect, flags)
        # 이미 인정한 쟁점은 관련 질문에 답할 수 있다. 새 인정은 앞의 자료 조건만 결정한다.
        flag_patterns = {
            "gang_drug": "약|수면|와인", "gang_visit": "차용|꽃병|재방문|원본",
            "yoon_money": "장부|횡령|빼돌|12억", "yoon_visit": "금고|재방문",
            "sera_draft": "초안|훔|서류", "cha_identity": "친자|친아들|사진|어머니",
            "seo_forgery": "위작|진품|판매|팔았", "seo_burn": "소각|벽난로|태웠|일기",
        }
        admissions = self.catalog.testimony["admissionEntries"]
        own_flags = {rule["flag"] for rule in self.catalog.findings if rule["suspectId"] == suspect}
        for flag, pattern in flag_patterns.items():
            if flag in flags and flag in own_flags and re.search(pattern, question) and flag in admissions:
                return [deepcopy(admissions[flag])]
        selectors = [("snoring", "코.*고|22:25"), ("missing-draft", "초안|봉투|분실"),
            ("dining", "식당|위스키"), ("white-glove", "흰.*장갑|22:40"), ("knock", "노크|22:50"),
            ("crying", "백세라|울"), ("absence", "화장실|거실|35"), ("fireplace", "벽난로|뒷모습|태웠"),
            ("breathing", "호흡|숨|살아"), ("room", "어디|방.*있"), ("meeting", "면담|언제|몇.*시|와인|혈압")]
        for key, pattern in selectors:
            match = next((entry for entry in movement if entry["key"] == key), None)
            if match and re.search(pattern, question):
                return [match]
        person = self.catalog.people[suspect]
        if re.search(r"누구|직업|몇.*살|나이|자기소개", question):
            return [{"key": "profile", "title": person["name"] + "의 자기소개", "text": person["statement"], "nature": "본인 진술"}]
        return []
````

