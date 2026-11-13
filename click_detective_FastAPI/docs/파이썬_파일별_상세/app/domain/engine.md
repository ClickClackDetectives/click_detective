# app/domain/engine.py 상세 설명

[문서 목차](../../../README.md) · [파일별 목차](../../README.md) · [현재 소스](../../../../app/domain/engine.py)

## 역할과 읽는 순서

자료 열람·진술·쟁점·추론·단계·고발 규칙. LLM은 이 상태를 직접 수정하지 않는다.

열람·정확한 추론 조합·단계 전환·최종 고발을 판정합니다. 고발은 1차부터 가능하고 증거 0개도 허용합니다. 핵심 추론과 원본 근거 연결은 채점 기준입니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## utc_now

[원본 8번째 줄](../../../../app/domain/engine.py#L8)

저장 시각을 타임존이 있는 ISO 문자열로 만든다.

### 입력과 처리

```python
def utc_now():
```

### 실제 코드

````python
def utc_now():
    """저장 시각을 타임존이 있는 ISO 문자열로 만든다."""
    return datetime.now(timezone.utc).isoformat()
````

## Engine

[원본 13번째 줄](../../../../app/domain/engine.py#L13)

정적 데이터와 실제 획득 기록만으로 판정하는 Python 게임 엔진.

## Engine.__init__

[원본 16번째 줄](../../../../app/domain/engine.py#L16)

내부 사건·규칙 저장소를 연결한다.

### 입력과 처리

```python
def __init__(self, catalog):
```

### 실제 코드

````python
def __init__(self, catalog):
        """내부 사건·규칙 저장소를 연결한다."""
        self.c = catalog
````

## Engine.initial

[원본 20번째 줄](../../../../app/domain/engine.py#L20)

새 수사는 새로운 ID로 시작한다. 예전 수사에 늦은 응답이 반영되지 않는다.

### 입력과 처리

```python
def initial(self, game_id):
```

### 실제 코드

````python
def initial(self, game_id):
        """새 수사는 새로운 ID로 시작한다. 예전 수사에 늦은 응답이 반영되지 않는다."""
        state = deepcopy(self.c.read("initial-state.json")["state"])
        state.update(id=game_id, startedAt=utc_now(), revision=0, scenarioVersion=self.c.version)
        return state
````

## Engine.require_active

[원본 26번째 줄](../../../../app/domain/engine.py#L26)

버전 변경과 종결 후 변경 요청을 거절한다.

### 입력과 처리

```python
def require_active(self, state):
```

주요 분기 조건은 `state['scenarioVersion'] != self.c.version`, `state['verdict']`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def require_active(self, state):
        """버전 변경과 종결 후 변경 요청을 거절한다."""
        if state["scenarioVersion"] != self.c.version:
            raise HTTPException(409, "scenario_version_conflict")
        if state["verdict"]:
            raise HTTPException(409, "이미 종결된 사건입니다.")
````

## Engine.examine

[원본 33번째 줄](../../../../app/domain/engine.py#L33)

현재 단계의 실제 자료만 열람한다. 중복은 개수·revision을 늘리지 않는다.

### 입력과 처리

```python
def examine(self, state, command):
```

주요 분기 조건은 `not record or record['phase'] > state['phase']`, `record['id'] not in state['examined']`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def examine(self, state, command):
        """현재 단계의 실제 자료만 열람한다. 중복은 개수·revision을 늘리지 않는다."""
        record = self.c.evidence.get(command.evidence_id)
        if not record or record["phase"] > state["phase"]:
            raise HTTPException(404, "현재 공개된 자료가 아닙니다.")
        if record["id"] not in state["examined"]:
            state["examined"].append(record["id"])
        return {"material_id": record["id"]}
````

## Engine.record_plan

[원본 42번째 줄](../../../../app/domain/engine.py#L42)

검증된 응답이 나온 뒤에만 질문·대화·쟁점·진술을 일괄 반영한다.

### 입력과 처리

```python
def record_plan(self, state, plan, response):
```

주요 분기 조건은 `rule['flag'] not in state['revealed']`, `entry['key'] == 'profile'`, `key in state['statements']`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def record_plan(self, state, plan, response):
        """검증된 응답이 나온 뒤에만 질문·대화·쟁점·진술을 일괄 반영한다."""
        state["questions"] += 1
        state["messages"].extend([
            {"suspectId": plan.suspect_id, "role": "user", "text": plan.question,
             "evidenceId": plan.material_id, "topicId": plan.topic},
            {"suspectId": plan.suspect_id, "role": "suspect", "text": response.reply,
             "finishReason": response.finish_reason, "modelVersion": response.model_version},
        ])
        for rule in plan.new_findings:
            if rule["flag"] not in state["revealed"]:
                state["revealed"].append(rule["flag"])
                state["contradictions"].append(rule["label"])
                state["findingDetails"].append({"title": rule["label"], "suspectId": plan.suspect_id,
                    "sourceRefs": plan.sources, "messageIndex": len(state["messages"]) - 1})
        for entry in plan.entries:
            if entry["key"] == "profile":
                continue
            key = plan.suspect_id + "-" + entry["key"]
            if key in state["statements"]:
                continue
            section = "다른 사람들에 대해" if (plan.topic or "").startswith("about-") else "그날 밤 당신의 행동"
            script = self.c.scripts["characters"][plan.suspect_id]
            state["statements"][key] = {
                "id": key, "code": f"ST-{len(state['statements']) + 1:03}", "speaker": plan.suspect_id,
                "topic": "admission" if plan.new_findings else plan.topic or "movement",
                "title": entry["title"], "excerpt": entry["text"], "nature": entry["nature"],
                "sourceRefs": deepcopy(plan.sources), "messageIndex": len(state["messages"]) - 1,
                "source": {"file": "01_대본_" + self.c.people[plan.suspect_id]["name"] + ".pdf",
                           "pages": script["sections"][section]["pages"], "section": section},
                **{field: deepcopy(entry[field]) for field in ("target", "time", "start", "end", "supersedes") if field in entry},
            }
        return {"reply": response.reply, "finish_reason": response.finish_reason,
                "model_version": response.model_version, "used_fact_ids": response.used_fact_ids}
````

## Engine.readable_source

[원본 77번째 줄](../../../../app/domain/engine.py#L77)

존재뿐 아니라 실제 획득·단계 조건도 검사한다.

### 입력과 처리

```python
def readable_source(self, state, source):
```

주요 분기 조건은 `kind == 'evidence'`, `not known`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def readable_source(self, state, source):
        """존재뿐 아니라 실제 획득·단계 조건도 검사한다."""
        kind, key = source["kind"], source["id"]
        if kind == "evidence":
            record = self.c.evidence.get(key)
            known = record and record["phase"] <= state["phase"] and key in state["examined"]
        else:
            known = key in state["statements" if kind == "testimony" else "derivedEvidence"]
        if not known:
            raise HTTPException(422, "직접 열람하거나 생성한 자료만 연결할 수 있습니다.")
````

## Engine.infer

[원본 88번째 줄](../../../../app/domain/engine.py#L88)

직접 선택한 정확한 조합과 단계가 일치하면 고정 결론을 만든다. LLM은 사용하지 않는다.

### 입력과 처리

```python
def infer(self, state, command):
```

주요 분기 조건은 `len(keys) != len(sources)`, `not rule`, `rule['phase'] != state['phase']`, `key not in state['derivedEvidence']`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def infer(self, state, command):
        """직접 선택한 정확한 조합과 단계가 일치하면 고정 결론을 만든다. LLM은 사용하지 않는다."""
        sources = [source.model_dump() for source in command.sources]
        keys = {(ref["kind"], ref["id"]) for ref in sources}
        if len(keys) != len(sources):
            raise HTTPException(422, "서로 다른 자료를 선택하세요.")
        for source in sources:
            self.readable_source(state, source)
        rule = next((rule for rule in self.c.inferences if {(ref["kind"], ref["id"]) for ref in rule["sources"]} == keys), None)
        if not rule:
            raise HTTPException(422, "선택한 자료만으로 뒷받침되는 연결을 찾지 못했습니다.")
        if rule["phase"] != state["phase"]:
            raise HTTPException(422, "이 추론의 조사 단계를 확인하세요.")
        key = "derived-" + rule["id"]
        if key not in state["derivedEvidence"]:
            leaves = {}
            for ref in sources:
                refs = state["derivedEvidence"][ref["id"]]["leafSources"] if ref["kind"] == "derived" else [ref]
                for leaf in refs:
                    leaves[(leaf["kind"], leaf["id"])] = deepcopy(leaf)
            state["derivedEvidence"][key] = {
                "id": key, "code": rule["code"], "kind": "derived", "type": "추론 증거", "title": rule["title"],
                "time": "", "summary": "확보한 자료의 연결로 도출한 수사관의 추론입니다.",
                "phase": state["phase"], "body": rule["body"], "sourceRefs": sources, "leafSources": list(leaves.values()),
                "investigationPhase": rule["phase"], "construction": "chain" if any(ref["kind"] == "derived" for ref in sources) else "base",
            }
        return deepcopy(state["derivedEvidence"][key])
````

## Engine.readiness

[원본 116번째 줄](../../../../app/domain/engine.py#L116)

입증 진행 개수를 계산한다. 진행도와 무관하게 미종결 수사는 고발할 수 있다.

### 입력과 처리

```python
def readiness(self, state):
```

### 실제 코드

````python
def readiness(self, state):
        """입증 진행 개수를 계산한다. 진행도와 무관하게 미종결 수사는 고발할 수 있다."""
        rules = self.c.rules["accusation"]
        inference = sum(key in state["derivedEvidence"] for key in rules["requiredInferenceIds"])
        findings = sum(flag in state["revealed"] for flag in rules["requiredFindingFlags"])
        return {"inference": inference, "findings": findings,
                "eligible": not bool(state["verdict"])}
````

## Engine.advance

[원본 124번째 줄](../../../../app/domain/engine.py#L124)

단계 전환 조건을 확인한 뒤 자동 자료와 단계를 함께 변경한다.

### 입력과 처리

```python
def advance(self, state, command):
```

주요 분기 조건은 `state['phase'] != 1`, `len(state['derivedEvidence']) < requirements['inference'] or len(set(state['contradictions'])) < requirements['findings']`, `key not in state['examined']`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def advance(self, state, command):
        """단계 전환 조건을 확인한 뒤 자동 자료와 단계를 함께 변경한다."""
        requirements = self.c.rules["secondRound"]["requirements"]
        if state["phase"] != 1:
            raise HTTPException(409, "이미 2차 조사가 진행 중입니다.")
        if len(state["derivedEvidence"]) < requirements["inference"] or len(set(state["contradictions"])) < requirements["findings"]:
            raise HTTPException(422, "2차 수사에는 추론 증거 2개와 심문 쟁점 2개 이상이 필요합니다.")
        state["phase"] = 2
        for key in self.c.rules["secondRound"]["automaticEvidenceIds"]:
            if key not in state["examined"]:
                state["examined"].append(key)
        return {"phase": 2}
````

## Engine.covered

[원본 137번째 줄](../../../../app/domain/engine.py#L137)

제출한 실제 추론의 원본 근거 중 실제 열람한 자료만 계산한다.

### 입력과 처리

```python
def covered(self, state, ids):
```

### 실제 코드

````python
def covered(self, state, ids):
        """제출한 실제 추론의 원본 근거 중 실제 열람한 자료만 계산한다."""
        return {ref["id"] for key in ids for ref in state["derivedEvidence"][key]["leafSources"]
                if ref["kind"] == "evidence" and ref["id"] in state["examined"]}
````

## Engine.accuse

[원본 142번째 줄](../../../../app/domain/engine.py#L142)

언제든 고발을 받아 채점한다. 부족한 입증은 제출 차단 대신 점수에 반영한다.

조사 단계·발견 쟁점 수·추론 개수는 제출 조건이 아니다. 제출한 ID가 있다면
실제 확보한 서로 다른 추론인지 검사하고, 핵심 근거 충족 여부로 채점한다.

### 입력과 처리

```python
def accuse(self, state, command):
```

주요 분기 조건은 `command.suspect_id not in self.c.people or command.motive not in {x['id'] for x in self.c.case['motiveOptions']} or command.method not in {x['id'] for x in self.c.case['methodOptions']}`, `len(set(ids)) != len(ids) or any((key not in state['derivedEvidence'] for key in ids))`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def accuse(self, state, command):
        """언제든 고발을 받아 채점한다. 부족한 입증은 제출 차단 대신 점수에 반영한다.

        조사 단계·발견 쟁점 수·추론 개수는 제출 조건이 아니다. 제출한 ID가 있다면
        실제 확보한 서로 다른 추론인지 검사하고, 핵심 근거 충족 여부로 채점한다.
        """
        if command.suspect_id not in self.c.people or command.motive not in {x["id"] for x in self.c.case["motiveOptions"]} or command.method not in {x["id"] for x in self.c.case["methodOptions"]}:
            raise HTTPException(422, "모든 고발 항목을 확인하세요.")
        ids = command.evidence_ids
        if len(set(ids)) != len(ids) or any(key not in state["derivedEvidence"] for key in ids):
            raise HTTPException(422, "확보한 서로 다른 추론 증거를 제출하세요.")
        covered = self.covered(state, ids)
        rules = self.c.rules["accusation"]
        core = all(key in ids for key in rules["requiredInferenceIds"]) and all(set(group) & covered for group in rules["coreEvidenceGroups"])
        answer = self.c.solution["solution"]
        flags = [command.suspect_id == answer["suspectId"], command.motive == answer["motive"], command.method == answer["method"], bool(core)]
        review = {"findings": [{"id": rule["flag"], "title": rule["label"], "discovered": rule["flag"] in state["revealed"]} for rule in self.c.findings],
                  "inference": [{"id": "derived-" + rule["id"], "title": rule["title"], "discovered": "derived-" + rule["id"] in state["derivedEvidence"], "submitted": "derived-" + rule["id"] in ids} for rule in self.c.inferences]}
        submitted = []
        for key in ids:
            own = self.covered(state, [key])
            contribution = [item for group in rules["coreEvidenceGroups"] for item in group if item in own]
            submitted.append({"id": key, "title": state["derivedEvidence"][key]["title"], "kind": "derived",
                              "contributes": bool(contribution), "coveredTitles": [self.c.evidence[item]["title"] for item in contribution]})
        missing = [{"id": "|".join(group), "title": " 또는 ".join(self.c.evidence[item]["title"] for item in group)}
                   for group in rules["coreEvidenceGroups"] if not set(group) & covered]
        missing += [{"id": key, "title": "필수 추론: " + state["derivedEvidence"].get(key, {}).get("title", key)} for key in rules["requiredInferenceIds"] if key not in ids]
        state["verdict"] = {"correct": all(flags), "score": sum(flags) * self.c.solution["pointsPerCheck"],
            "checks": [{"label": label, "correct": value} for label, value in zip(self.c.solution["checks"], flags)],
            "submittedEvidenceIds": ids, "evidenceAssessment": {"submitted": submitted, "missing": missing},
            "review": review, "explanation": self.c.solution["explanation"]}
        return deepcopy(state["verdict"])
````

