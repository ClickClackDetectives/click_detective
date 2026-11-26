# `app/investigation/dto/investigation_interrogation_plan_dto.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/dto/investigation_interrogation_plan_dto.py)

수사 규칙이 승인한 심문 계획을 대화 서비스에 전달한다.

## `ReplyPlan`

[소스 선언](../../../../../app/investigation/dto/investigation_interrogation_plan_dto.py#L7)

```python
class ReplyPlan:
    ...
```

생성할 사실과 확정할 구조화 기록을 분리한 요청별 계획.

**인자**

- suspect_id (str): 심문 대상 인물의 식별자.
- question (str): 사용자가 입력한 질문 원문.
- topic (str | None): 질문에서 명시할 주제 식별자.
- entries (list[dict]): 게임 기록에 반영할 승인 진술.
- facts (list[dict]): 모델에 제공할 승인 사실.
- new_findings (list[dict]): 이번 심문으로 새로 공개할 쟁점.
- sources (list[dict]): 진술과 쟁점의 실제 근거.
- material_id (str | None): 이번 심문에 제시한 자료 식별자.

**반환값**

- ReplyPlan: 위 역할을 수행하도록 생성된 객체.
