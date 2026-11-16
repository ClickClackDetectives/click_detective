# `app/dialogue/validation_agent/prompt.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/validation_agent/prompt.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 85줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

후보 대사를 검사할 모델 지시와 자료를 준비한다.

## 함께 읽을 코드

- [app/config.py](../../config.md)
- [app/dialogue/preprocess_agent/prompt.py](../preprocess_agent/prompt.md)
- [app/dialogue/schemas.py](../schemas.md)
- [app/dialogue/validation_agent/verification_units.py](verification_units.md)
- [app/dialogue/validation_agent/semantic_verification.py](semantic_verification.md)

## `build_verification_messages`

[소스 선언 위치](../../../../../app/dialogue/validation_agent/prompt.py#L30)

```python
def build_verification_messages(
    request: CharacterReplyRequest,
    settings: Settings,
    reply: str,
) -> list[dict[str, str]]:
    ...
```

별도 검증 호출에 승인 사실·생성 대사·관련 이력만 전달한다. 숨겨진 정답은 넣지 않는다.

**파라미터**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- settings (Settings): 모델 실행과 검색에 사용할 설정.
- reply (str): 의미를 검사하거나 문장으로 나눌 후보 대사.

**반환값**

list[dict[str, str]]: 승인 문장과 후보 문장을 비교할 검증용 프롬프트.
