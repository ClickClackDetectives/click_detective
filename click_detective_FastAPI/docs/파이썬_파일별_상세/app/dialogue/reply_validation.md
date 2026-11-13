# app/dialogue/reply_validation.py 상세 설명

[문서 목차](../../../README.md) · [파일별 목차](../../README.md) · [현재 소스](../../../../app/dialogue/reply_validation.py)

## 역할과 읽는 순서

응답 검증과 고정 대사 조립. HTTP·로컬 모델이 공통으로 사용한다.

ID·필수 사실을 검사합니다. local의 검증된 stop은 require_verbatim=False, fixture/fallback은 원문 보존 검사입니다. 이 파일 하나로 의미 검증 전체를 대체할 수 없습니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## 모듈 설정과 상수

```python
NO_FACTS = "지금 말씀드릴 수 있는 추가 내용은 없습니다."
FIXED_MODEL_VERSION = "fixed-v1"
```

이 값은 코드 선언입니다. 실제 .env 비밀값이나 수사 DB 값은 여기에 읽어 넣지 않았습니다.

## validate_generation

[원본 9번째 줄](../../../../app/dialogue/reply_validation.py#L9)

식별 정보·사실 ID·필수 사실을 검사한다. 고정 모드는 원문까지 대조한다. 실패하면 ValueError를 낸다.

require_verbatim=False는 의미 검증을 별도로 수행하는 local 그래프에서만 사용한다.
ID 검사만으로 내용이 참이라고 보장하지 않는다.
이 검사는 임의의 추가 문장이 참인지 판별하지는 않는다. 그 범위는 조립 단계에서
승인 원문만 사용하도록 제한한다.

### 입력과 처리

```python
def validate_generation(
```

주요 분기 조건은 `response_identity != request_identity`, `has_duplicate_ids or has_unapproved_ids`, `not required_fact_ids.issubset(used_fact_ids)`, `not response.reply.strip() or (require_verbatim and missing_fact_text)`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def validate_generation(
    request: CharacterReplyRequest,
    response: CharacterReplyResponse,
    *,
    require_verbatim: bool = True,
) -> None:
    """식별 정보·사실 ID·필수 사실을 검사한다. 고정 모드는 원문까지 대조한다. 실패하면 ValueError를 낸다.

    require_verbatim=False는 의미 검증을 별도로 수행하는 local 그래프에서만 사용한다.
    ID 검사만으로 내용이 참이라고 보장하지 않는다.
    이 검사는 임의의 추가 문장이 참인지 판별하지는 않는다. 그 범위는 조립 단계에서
    승인 원문만 사용하도록 제한한다.
    """
    request_identity = (request.request_id, request.suspect_id, request.state_revision)
    response_identity = (response.request_id, response.suspect_id, response.state_revision)
    if response_identity != request_identity:
        raise ValueError("Response identity mismatch")

    allowed_fact_texts = {fact.id: fact.text for fact in request.allowed_facts}
    used_fact_ids = set(response.used_fact_ids)
    required_fact_ids = set(request.required_fact_ids)

    has_duplicate_ids = len(response.used_fact_ids) != len(used_fact_ids)
    has_unapproved_ids = not used_fact_ids.issubset(allowed_fact_texts)
    if has_duplicate_ids or has_unapproved_ids:
        raise ValueError("Invalid used fact IDs")
    if not required_fact_ids.issubset(used_fact_ids):
        raise ValueError("Missing required facts")

    missing_fact_text = any(
        allowed_fact_texts[fact_id] not in response.reply
        for fact_id in response.used_fact_ids
    )
    if not response.reply.strip() or (require_verbatim and missing_fact_text):
        raise ValueError("Missing verbatim fact text")
````

## assemble_reply

[원본 47번째 줄](../../../../app/dialogue/reply_validation.py#L47)

모든 승인 사실을 순서대로 붙인다. 사실이 없으면 중립 대사를 준다.

### 입력과 처리

```python
def assemble_reply(request: CharacterReplyRequest) -> str:
```

주요 분기 조건은 `not request.allowed_facts`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def assemble_reply(request: CharacterReplyRequest) -> str:
    """모든 승인 사실을 순서대로 붙인다. 사실이 없으면 중립 대사를 준다."""
    if not request.allowed_facts:
        return NO_FACTS

    sentences = [fact.text for fact in request.allowed_facts]
    return " ".join(sentences)
````

