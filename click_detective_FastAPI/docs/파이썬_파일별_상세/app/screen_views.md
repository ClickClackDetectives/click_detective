# app/screen_views.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../app/screen_views.py)

## 역할과 읽는 순서

원본 Next.js 자료실의 검색·분류 결과를 FastAPI에서 구성하는 표시 전용 서비스.

아래 함수의 입력과 조건을 먼저 읽고 연결된 호출을 원본 소스에서 따라가세요.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## ScreenViews

[원본 4번째 줄](../../../app/screen_views.py#L4)

게임 규칙을 바꾸지 않고 같은 상태를 원본 화면이 요구하는 목록으로 변환한다.

## ScreenViews.__init__

[원본 7번째 줄](../../../app/screen_views.py#L7)

사건 원본과 공개 상태 변환기를 받아 중복된 프런트엔드 데이터 처리를 없앤다.

### 입력과 처리

```python
def __init__(self, catalog, presenter):
```

### 실제 코드

````python
def __init__(self, catalog, presenter):
        """사건 원본과 공개 상태 변환기를 받아 중복된 프런트엔드 데이터 처리를 없앤다."""
        self.c, self.presenter = catalog, presenter
````

## ScreenViews.evidence

[원본 11번째 줄](../../../app/screen_views.py#L11)

물증·문서를 장소별로 분류한다. 검색은 원본의 공백·대소문자 동작을 유지한다.

### 입력과 처리

```python
def evidence(self, state, search="", place="all"):
```

주요 분기 조건은 `records and place in {'all', name}`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
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
````

## ScreenViews.testimonies

[원본 26번째 줄](../../../app/screen_views.py#L26)

최초 진술·집사 문서·획득 증언·질문/답변 쌍을 원본 화면과 같은 순서로 검색한다.

### 입력과 처리

```python
def testimonies(self, state, search="", person="all"):
```

주요 분기 조건은 `person not in {'all', key}`, `not initial or query not in (name + ' ' + initial).lower()`, `key == 'butler'`, `initial or pairs or records or acquired`, `question['role'] != 'user'`, `answer and answer['role'] != 'suspect'` 등입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
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
````

## ScreenViews.inference

[원본 68번째 줄](../../../app/screen_views.py#L68)

획득한 실제 출처를 자료 종류와 검색어로 골라 원본 추론 선택창에 제공한다.

### 입력과 처리

```python
def inference(self, state, search="", category="evidence"):
```

### 실제 코드

````python
def inference(self, state, search="", category="evidence"):
        """획득한 실제 출처를 자료 종류와 검색어로 골라 원본 추론 선택창에 제공한다."""
        sources = self.presenter.state(state)["inferenceSources"]
        query = search.strip().lower()
        return {"visible": [item for item in sources if item["category"] == category and
                query in (item["code"] + " " + item["title"] + " " + item["context"]).lower()]}
````

