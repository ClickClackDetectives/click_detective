# app/dialogue/critical_facts.py 상세 설명

[문서 목차](../../../README.md) · [파일별 목차](../../README.md) · [현재 소스](../../../../app/dialogue/critical_facts.py)

## 역할과 읽는 순서

명시적 수량·시각 귀속·일부 목적 표현의 규칙 검사. 일반 의미 이해를 대신하지 않는다.

정규식으로 읽을 수 있는 범위만 다룬다. 생략·동의어가 애매하면 검증 불가로 거절할
수 있으므로 원래 승인 의미를 유지한 재서술을 회귀 평가로 함께 확인해야 한다.

수량·시각·행동 귀속·일부 부정/목적/관찰 한계를 좁은 규칙으로 확인합니다. 한국어 전체를 이해하지 않으므로 정상 동의어를 거절할 수도 있습니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## 모듈 설정과 상수

```python
NATIVE_NUMBERS = {"한": 1, "두": 2, "세": 3, "네": 4, "다섯": 5, "여섯": 6,
                  "일곱": 7, "여덟": 8, "아홉": 9, "열": 10}
COUNT = re.compile(r"(?<![가-힣0-9])([0-9]+|한|두|세|네|다섯|여섯|일곱|여덟|아홉|열)\s*(알|억(?:\s*원)?|년|점|명|개)")
CLOCK = re.compile(r"(?<!\d)(\d{1,2})(?:\s*시(?:\s*(\d{1,2})\s*분)?|:(\d{2}))")
```

이 값은 코드 선언입니다. 실제 .env 비밀값이나 수사 DB 값은 여기에 읽어 넣지 않았습니다.

## quantity_anchors

[원본 19번째 줄](../../../../app/dialogue/critical_facts.py#L19)

두 알과 2알 등을 같은 값으로 읽는다. 모든 한국어 수사를 해석하지는 않는다.

### 입력과 처리

```python
def quantity_anchors(text: str) -> set[tuple[int, str]]:
```

### 실제 코드

````python
def quantity_anchors(text: str) -> set[tuple[int, str]]:
    """두 알과 2알 등을 같은 값으로 읽는다. 모든 한국어 수사를 해석하지는 않는다."""
    return {(int(number) if number.isdigit() else NATIVE_NUMBERS[number], re.sub(r"\s+", "", unit).replace("억원", "억"))
            for number, unit in COUNT.findall(text)}
````

## time_anchors

[원본 25번째 줄](../../../../app/dialogue/critical_facts.py#L25)

11시 2분·23:02의 시계상 위치를 비교한다. 오전/오후 추론은 모델에 남긴다.

### 입력과 처리

```python
def time_anchors(text: str) -> set[tuple[int, int]]:
```

### 실제 코드

````python
def time_anchors(text: str) -> set[tuple[int, int]]:
    """11시 2분·23:02의 시계상 위치를 비교한다. 오전/오후 추론은 모델에 남긴다."""
    return {(int(hour) % 12, int(korean or colon or 0)) for hour, korean, colon in CLOCK.findall(text)}
````

## time_actions

[원본 30번째 줄](../../../../app/dialogue/critical_facts.py#L30)

같은 문장에 명시된 숨기기·방문 행동과 시각을 연결한다. 문장 밖 추론은 하지 않는다.

### 입력과 처리

```python
def time_actions(text: str) -> set[tuple[tuple[int, int], str]]:
```

주요 분기 조건은 `re.search('숨[기겼겨긴]|감[추췄춘춰]', part.text)`, `re.search('(?:서재|방|현장)(?:에|로)\\s*(?:갔|왔|찾아|들어)|방문', part.text)`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def time_actions(text: str) -> set[tuple[tuple[int, int], str]]:
    """같은 문장에 명시된 숨기기·방문 행동과 시각을 연결한다. 문장 밖 추론은 하지 않는다."""
    result = set()
    for part in candidate_sentences(text):
        actions = set()
        if re.search(r"숨[기겼겨긴]|감[추췄춘춰]", part.text):
            actions.add("hide")
        if re.search(r"(?:서재|방|현장)(?:에|로)\s*(?:갔|왔|찾아|들어)|방문", part.text):
            actions.add("visit")
        result.update((clock, action) for clock in time_anchors(part.text) for action in actions)
    return result
````

## postponement_target

[원본 43번째 줄](../../../../app/dialogue/critical_facts.py#L43)

발표·공개·일정·회의를 미루려는 명시적 목적 표현만 읽는다.

### 입력과 처리

```python
def postponement_target(text: str) -> str | None:
```

주요 분기 조건은 `not re.search('(?:미루|늦추|연기하|지연시키)(?:려|기\\s*위해|고자)', text)`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def postponement_target(text: str) -> str | None:
    """발표·공개·일정·회의를 미루려는 명시적 목적 표현만 읽는다."""
    if not re.search(r"(?:미루|늦추|연기하|지연시키)(?:려|기\s*위해|고자)", text):
        return None
    match = re.search(r"발표|공개|일정|회의", text)
    return match.group() if match else None
````

## critical_claim_error

[원본 51번째 줄](../../../../app/dialogue/critical_facts.py#L51)

원문에 없는 명시적 수량·시각·행동 귀속과 읽을 수 있는 필수 목적 누락을 거절한다.

새 사건 사실의 근거는 allowed_facts뿐이다. 질문·인물 프로필·제시 자료·이력에서
숫자나 행동을 가져왔다고 승인하지 않는다. 오류에는 원문을 넣지 않는다.

### 입력과 처리

```python
def critical_claim_error(request: CharacterReplyRequest, reply: str) -> str | None:
```

주요 분기 조건은 `not quantity_anchors(reply).issubset(quantity_anchors(approved))`, `not time_anchors(reply).issubset(time_anchors(approved))`, `not time_actions(reply).issubset(time_actions(approved))`, `negative and positive`, `unit.fact_id not in required`, `not predicate_anchors(unit.text).issubset(predicate_anchors(reply))` 등입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def critical_claim_error(request: CharacterReplyRequest, reply: str) -> str | None:
    """원문에 없는 명시적 수량·시각·행동 귀속과 읽을 수 있는 필수 목적 누락을 거절한다.

    새 사건 사실의 근거는 allowed_facts뿐이다. 질문·인물 프로필·제시 자료·이력에서
    숫자나 행동을 가져왔다고 승인하지 않는다. 오류에는 원문을 넣지 않는다.
    """
    approved = " ".join(fact.text for fact in request.allowed_facts)
    if not quantity_anchors(reply).issubset(quantity_anchors(approved)):
        return "unapproved_quantity_claim"
    if not time_anchors(reply).issubset(time_anchors(approved)):
        return "unapproved_time_claim"
    if not time_actions(reply).issubset(time_actions(approved)):
        return "time_action_binding_changed"
    for container in ("병", "잔"):
        negative = re.search(re.escape(container) + r"(?:에|에는|에도)\s*넣지\s*않", approved)
        positive = re.search(re.escape(container) + r"(?:에|에는|에도)\s*넣었", reply)
        if negative and positive:
            return "container_negation_changed"
    required = set(request.required_fact_ids)
    for unit in build_verification_units(request):
        if unit.fact_id not in required:
            continue
        if not predicate_anchors(unit.text).issubset(predicate_anchors(reply)):
            return "required_action_or_limit_missing"
        target = postponement_target(unit.text)
        if target and not any(postponement_target(part.text) == target for part in candidate_sentences(reply)):
            return "required_purpose_unverified"
        if not time_actions(unit.text).issubset(time_actions(reply)):
            return "required_time_action_missing"
    return None
````

## critical_evidence_error

[원본 83번째 줄](../../../../app/dialogue/critical_facts.py#L83)

모델이 true라고 해도 선택한 실제 근거에서 명시적 수량·시각이 빠지면 거절한다.

### 입력과 처리

```python
def critical_evidence_error(unit_text: str, evidence_text: str) -> str | None:
```

주요 분기 조건은 `not predicate_anchors(unit_text).issubset(predicate_anchors(evidence_text))`, `not quantity_anchors(unit_text).issubset(quantity_anchors(evidence_text))`, `not time_anchors(unit_text).issubset(time_anchors(evidence_text))`, `not time_actions(unit_text).issubset(time_actions(evidence_text))`, `target and (not any((postponement_target(part.text) == target for part in candidate_sentences(evidence_text))))`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def critical_evidence_error(unit_text: str, evidence_text: str) -> str | None:
    """모델이 true라고 해도 선택한 실제 근거에서 명시적 수량·시각이 빠지면 거절한다."""
    if not predicate_anchors(unit_text).issubset(predicate_anchors(evidence_text)):
        return "evidence_action_or_limit_missing"
    if not quantity_anchors(unit_text).issubset(quantity_anchors(evidence_text)):
        return "evidence_quantity_missing"
    if not time_anchors(unit_text).issubset(time_anchors(evidence_text)):
        return "evidence_time_missing"
    if not time_actions(unit_text).issubset(time_actions(evidence_text)):
        return "evidence_time_action_missing"
    target = postponement_target(unit_text)
    if target and not any(postponement_target(part.text) == target for part in candidate_sentences(evidence_text)):
        return "evidence_purpose_unverified"
    return None
````

## predicate_anchors

[원본 99번째 줄](../../../../app/dialogue/critical_facts.py#L99)

방문·회수 의도·관찰 한계·흔들기·무반응·맥 확인 한계·질문의 명시적 표현을 읽는다.

알려진 누락 사례를 위한 제한된 표현 사전이며 한국어 전체의 논리 분석은 아니다.
같은 문장 안의 주체나 시제까지 완전하게 보장하지 않는다.

### 입력과 처리

```python
def predicate_anchors(text: str) -> set[str]:
```

주요 분기 조건은 `re.search('(?:서재|방|현장|금고)(?:에|로)[^.!?]*(?:갔|왔|다녀|들어)|방문', sentence)`, `re.search('가지러|찾으러|회수하러|가져오려|되찾으려', sentence)`, `re.search('(?:상태|모습)[^.!?]*(?:확신|확인|판단)[^.!?]*(?:못|않)', sentence)`, `re.search('흔들', sentence)`, `re.search('반응[^.!?]*(?:없|않)|응답[^.!?]*없', sentence)`, `re.search('(?:맥|맥박)[^.!?]*(?:못|확실하지|불확실)', sentence)` 등입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def predicate_anchors(text: str) -> set[str]:
    """방문·회수 의도·관찰 한계·흔들기·무반응·맥 확인 한계·질문의 명시적 표현을 읽는다.

    알려진 누락 사례를 위한 제한된 표현 사전이며 한국어 전체의 논리 분석은 아니다.
    같은 문장 안의 주체나 시제까지 완전하게 보장하지 않는다.
    """
    result = set()
    for part in candidate_sentences(text):
        sentence = part.text
        if re.search(r"(?:서재|방|현장|금고)(?:에|로)[^.!?]*(?:갔|왔|다녀|들어)|방문", sentence):
            result.add("visit")
        if re.search(r"가지러|찾으러|회수하러|가져오려|되찾으려", sentence):
            result.add("retrieve_intent")
        if re.search(r"(?:상태|모습)[^.!?]*(?:확신|확인|판단)[^.!?]*(?:못|않)", sentence):
            result.add("observation_uncertain")
        if re.search(r"흔들", sentence):
            result.add("shake")
        if re.search(r"반응[^.!?]*(?:없|않)|응답[^.!?]*없", sentence):
            result.add("no_response")
        if re.search(r"(?:맥|맥박)[^.!?]*(?:못|확실하지|불확실)", sentence):
            result.add("pulse_uncertain")
        if re.search(r"물었|물어봤|질문[^.!?]*했|여쭤봤|여쭈었", sentence):
            result.add("question")
    return result
````

