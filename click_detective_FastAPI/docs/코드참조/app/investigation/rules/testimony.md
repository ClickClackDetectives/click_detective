# `app/investigation/rules/testimony.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/investigation/rules/testimony.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 87줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

승인된 심문 결과를 대화·쟁점·진술 기록에 반영한다.

## `record_plan`

[소스 선언 위치](../../../../../app/investigation/rules/testimony.py#L6)

```python
def record_plan(catalog, state, plan, response):
    ...
```

검증된 응답이 나온 뒤에만 질문·대화·쟁점·진술을 일괄 반영한다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- plan: 게임 규칙이 승인한 사실과 기록 예정 정보를 담은 계획.
- response: 검사하거나 저장할 최종 대사 응답.

**반환값**

dict: 기록한 대사, 종료 사유, 모델 버전과 사용 사실 ID.
