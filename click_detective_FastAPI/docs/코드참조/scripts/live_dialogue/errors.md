# `scripts/live_dialogue/errors.py`

[코드 참조 목차](../../README.md) · [스크립트 목차](../README.md) · [실제 소스](../../../../scripts/live_dialogue/errors.py)

실서버 대화 검사 실패를 구분한다.

## `LiveTestFailure`

[소스 선언](../../../../scripts/live_dialogue/errors.py#L4)

```python
class LiveTestFailure(RuntimeError):
    ...
```

HTTP 오류 또는 실제 LLM 응답 조건 불일치를 보고서에 남기기 위한 예외.

**인자**

- 없음.

**반환값**

- LiveTestFailure: 위 역할을 수행하도록 생성된 객체.
