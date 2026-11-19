# `app/dialogue/validation_agent_v1/verification_prompting.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/validation_agent_v1/verification_prompting.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 65줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

전체 승인 문맥을 유지하면서 검사할 문장 묶음과 재요청 지시를 만든다.

## 함께 읽을 코드

- [app/dialogue/validation_agent_v1/prompt.py](prompt.md)
- [app/dialogue/validation_agent_v1/semantic_verification.py](semantic_verification.md)

## `build_batch_messages`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/verification_prompting.py#L9)

```python
def build_batch_messages(request, settings, reply, batch):
    ...
```

이번 배치에서 확인할 항목을 검증 프롬프트에 지정한다.

**파라미터**

- request: 원래 승인 사실과 필수 사실 ID를 담은 대화 요청.
- settings: 이력 개수 등 프롬프트 구성 설정.
- reply: 검사할 후보 대사 원문.
- batch: 이번 호출에서 검사할 승인 문장 목록.

**반환값**

list[dict[str, str]]: 전체 승인 사실과 이번 검사 항목을 담은 프롬프트.

## `build_report_retry`

[소스 선언 위치](../../../../../app/dialogue/validation_agent_v1/verification_prompting.py#L44)

```python
def build_report_retry(reply, batch, error):
    ...
```

같은 후보에 대해 올바른 형식의 검사표를 다시 요청한다.

**파라미터**

- reply: 재생성하지 않고 그대로 검사할 후보 대사.
- batch: 빠짐없이 확인해야 할 승인 문장 목록.
- error: 직전 보고서의 형식 오류 코드와 상세 사유.

**반환값**

dict[str, str]: 검증 프롬프트 끝에 추가할 사용자 역할 지시문.
