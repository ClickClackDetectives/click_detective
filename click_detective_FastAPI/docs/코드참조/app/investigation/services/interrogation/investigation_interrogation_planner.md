# `app/investigation/services/interrogation/investigation_interrogation_planner.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/investigation/services/interrogation/investigation_interrogation_planner.py)

게임 규칙으로 공개 가능한 심문 진술과 쟁점을 준비한다.

## `facts_from_entries`

[소스 선언](../../../../../../app/investigation/services/interrogation/investigation_interrogation_planner.py#L19)

```python
def facts_from_entries(suspect_id, entries):
    ...
```

수사 기록용 진술을 생성에 쓸 승인 사실로 변환한다.

**인자**

- suspect_id: 진술을 한 인물의 식별자.
- entries: 현재 공개 상태에서 선택된 원문 진술.
**반환값**

- list[dict]: 생성과 검증에 사용하는 승인 사실.

## `Planner`

[소스 선언](../../../../../../app/investigation/services/interrogation/investigation_interrogation_planner.py#L38)

```python
class Planner:
    ...
```

자료 획득·인물별 누적 제시·인정 상태로 이번에 말할 사실만 고른다.

**인자**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

**반환값**

- Planner: 위 역할을 수행하도록 생성된 객체.

## `Planner.__init__`

[소스 선언](../../../../../../app/investigation/services/interrogation/investigation_interrogation_planner.py#L48)

```python
def __init__(self, catalog):
    ...
```

현재 사건의 서버 전용 템플릿을 사용한다.

**인자**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

**반환값**

- None: 필요한 설정과 초기값을 저장한다.

## `Planner.movement`

[소스 선언](../../../../../../app/investigation/services/interrogation/investigation_interrogation_planner.py#L59)

```python
def movement(self, suspect, flags):
    ...
```

인정 플래그 조합에 맞는 동선 원문만 선택한다. 후보 전체를 모델에 주지 않는다.

**인자**

- suspect: 심문 대상 인물의 식별자.
- flags: 현재까지 인정되거나 공개된 쟁점 식별자 목록.

**반환값**

- list[dict]: 현재 인정 상태에 맞는 동선 진술.

## `Planner.resolve_topic`

[소스 선언](../../../../../../app/investigation/services/interrogation/investigation_interrogation_planner.py#L71)

```python
def resolve_topic(self, suspect, question, explicit):
    ...
```

명시적 주제는 허용 목록으로 검사하고 자유 입력은 알려진 주제만 추정한다.

**인자**

- suspect: 심문 대상 인물의 식별자.
- question: 사용자가 입력한 질문 원문.
- explicit: 사용자가 명시한 질문 주제. 없으면 질문에서 추정한다.

**반환값**

- str | None: 허용된 질문 주제. 추정할 수 없으면 None.

## `Planner.expand_material`

[소스 선언](../../../../../../app/investigation/services/interrogation/investigation_interrogation_planner.py#L100)

```python
def expand_material(self, state, material_id):
    ...
```

열람한 원본 또는 실제 생성한 추론만 제시하도록 허용한다.

**인자**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- material_id: 이번 심문에 제시한 자료 식별자.

**반환값**

- list[dict]: 제시 자료를 구성하는 실제 원본 출처.

## `Planner.prepare`

[소스 선언](../../../../../../app/investigation/services/interrogation/investigation_interrogation_planner.py#L121)

```python
def prepare(self, state, command, *, search_free=False):
    ...
```

질문·자료를 검사하고 원래 상태를 바꾸지 않은 채 승인 계획을 반환한다.

**인자**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
- search_free: 자유 질문의 진술 선택을 벡터 검색에 맡길지 여부.

**반환값**

- ReplyPlan: 공개할 사실과 저장할 진술·쟁점 정보. 입력 상태는 확정 변경하지 않는다.

## `Planner.free_entries`

[소스 선언](../../../../../../app/investigation/services/interrogation/investigation_interrogation_planner.py#L194)

```python
def free_entries(self, suspect, question, flags):
    ...
```

자유 질문을 공개 동선·관계·이미 인정한 진술에 연결한다. 미승인 비밀은 선택하지 않는다.

**인자**

- suspect: 심문 대상 인물의 식별자.
- question: 사용자가 입력한 질문 원문.
- flags: 현재까지 인정되거나 공개된 쟁점 식별자 목록.

**반환값**

- list[dict]: 질문과 관련하여 공개 가능한 진술. 없으면 빈 목록.
