# `app/investigation/services/rules/investigation_testimony_rules.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/investigation/services/rules/investigation_testimony_rules.py)

승인된 심문 결과를 대화·쟁점·진술 기록에 반영한다.

## `record_plan`

[소스 선언](../../../../../../app/investigation/services/rules/investigation_testimony_rules.py#L6)

```python
def record_plan(catalog, state, plan, response):
    ...
```

질문 차감 후 검증된 응답으로 대화·쟁점·진술을 일괄 반영한다.

**인자**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- plan: 게임 규칙이 승인한 사실과 기록 예정 정보를 담은 계획.
- response: 검사하거나 저장할 최종 대사 응답.

**반환값**

- dict: 기록한 대사, 종료 사유, 모델 버전과 사용 사실 ID.
