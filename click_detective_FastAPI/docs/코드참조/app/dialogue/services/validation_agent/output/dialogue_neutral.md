# `app/dialogue/services/validation_agent/output/dialogue_neutral.py`

[코드 참조 목차](../../../../../README.md) · [도메인 목차](../../../README.md) · [실제 소스](../../../../../../../app/dialogue/services/validation_agent/output/dialogue_neutral.py)

질문에 드러난 주제에 맞춰 검증에 사용할 고정 중립 대사를 선택한다.

## `classify_neutral_question`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/output/dialogue_neutral.py#L104)

```python
def classify_neutral_question(question: str) -> str:
    ...
```

질문에서 직접 언급한 주제를 찾는다.

**인자**

- question: 플레이어 질문 원문.

**반환값**

- str: 수사 범위 밖, 단일 주제 또는 공통 문구 카테고리.

## `select_neutral_reply`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/output/dialogue_neutral.py#L125)

```python
def select_neutral_reply(request: CharacterReplyRequest) -> tuple[str, str]:
    ...
```

승인 여부와 질문에 맞춰 같은 요청에는 같은 고정 대사를 고른다.

**인자**

- request: 질문, 승인 사실과 재시도 식별자를 담은 요청.

**반환값**

- tuple[str, str]: 중립 카테고리와 선택한 대사.
