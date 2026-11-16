# `scripts/live_dialogue/errors.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../scripts/live_dialogue/errors.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 12줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

실서버 대화 검사 실패를 구분한다.

## `LiveTestFailure`

[소스 선언 위치](../../../../scripts/live_dialogue/errors.py#L4)

```python
class LiveTestFailure(RuntimeError):
    ...
```

HTTP 오류 또는 실제 LLM 응답 조건 불일치를 보고서에 남기기 위한 예외.

**파라미터**

- 없음.

**반환값**

LiveTestFailure: 위 역할을 수행하도록 생성된 객체.
