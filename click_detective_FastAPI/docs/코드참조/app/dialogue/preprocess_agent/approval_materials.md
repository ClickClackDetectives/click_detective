# `app/dialogue/preprocess_agent/approval_materials.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/preprocess_agent/approval_materials.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 66줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

심문 대상에게 제시한 자료와 새로 공개할 쟁점을 고른다.

## `collect_materials`

[소스 선언 위치](../../../../../app/dialogue/preprocess_agent/approval_materials.py#L4)

```python
def collect_materials(planner, state, command):
    ...
```

과거와 현재의 제시 자료를 중복 없이 모으고 원본 출처를 확인한다.

**파라미터**

- planner: 자료의 획득 조건을 확인할 승인 계획 담당자.
- state: 현재 수사의 대화와 획득 자료 정보.
- command: 대상 인물과 이번에 제시한 자료를 담은 심문 입력.

**반환값**

tuple: 원본 증거 ID 집합과 제시 자료의 출처 목록.

## `collect_findings`

[소스 선언 위치](../../../../../app/dialogue/preprocess_agent/approval_materials.py#L40)

```python
def collect_findings(catalog, state, command, physical_ids):
    ...
```

이번 자료 제시로 새롭게 공개할 수 있는 쟁점을 고른다.

**파라미터**

- catalog: 인물별 쟁점 규칙을 가진 사건 데이터.
- state: 이미 공개된 쟁점을 담은 수사 상태.
- command: 대상 인물과 현재 제시 자료를 담은 심문 입력.
- physical_ids: 실제 획득한 제시 자료의 원본 증거 ID 집합.

**반환값**

list[dict]: 아직 공개되지 않았고 근거 조건이 충족된 쟁점 규칙.
