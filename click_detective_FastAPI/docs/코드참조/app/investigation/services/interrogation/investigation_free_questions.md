# `app/investigation/services/interrogation/investigation_free_questions.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/investigation/services/interrogation/investigation_free_questions.py)

인정 상태와 자유 질문에 맞는 공개 진술을 고른다.

## `movement`

[소스 선언](../../../../../../app/investigation/services/interrogation/investigation_free_questions.py#L7)

```python
def movement(catalog, suspect, flags):
    ...
```

인정 플래그 조합에 맞는 동선 원문만 선택한다. 후보 전체를 모델에 주지 않는다.

**인자**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- suspect: 심문 대상 인물의 식별자.
- flags: 현재까지 인정되거나 공개된 쟁점 식별자 목록.

**반환값**

- list[dict]: 현재 인정 상태에 맞는 동선 진술.

## `excluded_free_question`

[소스 선언](../../../../../../app/investigation/services/interrogation/investigation_free_questions.py#L33)

```python
def excluded_free_question(question):
    ...
```

자유 진술 검색에서 제외해 온 질문 표현을 확인한다.

**인자**

- question: 심문 입력 원문.
**반환값**

- bool: 기존 자유 질문 제외 규칙에 해당하는지 여부.

## `free_entries`

[소스 선언](../../../../../../app/investigation/services/interrogation/investigation_free_questions.py#L46)

```python
def free_entries(catalog, suspect, question, flags):
    ...
```

자유 질문을 공개 동선·관계·이미 인정한 진술에 연결한다. 미승인 비밀은 선택하지 않는다.

**인자**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- suspect: 심문 대상 인물의 식별자.
- question: 사용자가 입력한 질문 원문.
- flags: 현재까지 인정되거나 공개된 쟁점 식별자 목록.

**반환값**

- list[dict]: 질문과 관련하여 공개 가능한 진술. 없으면 빈 목록.
