# app/dialogue/meaning_guards.py 상세 설명

[문서 목차](../../../README.md) · [파일별 목차](../../README.md) · [현재 소스](../../../../app/dialogue/meaning_guards.py)

## 역할과 읽는 순서

알려진 한국어 질문 주체 역전의 좁은 규칙 방어. 일반적인 의미 검증을 대체하지 않는다.

아래 함수의 입력과 조건을 먼저 읽고 연결된 호출을 원본 소스에서 따라가세요.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## has_question_actor_reversal

[원본 6번째 줄](../../../../app/dialogue/meaning_guards.py#L6)

질문한 역할이 후보에서 질문받는 대상으로 바뀐 명시적 패턴을 탐지한다.

예: '기자인데 ... 물었습니다' → '기자님에게 ... 질문을 했습니다'.
한국어 전체를 해석하는 문법 분석기가 아니므로 이 패턴 밖은 의미 검증에 맡긴다.

### 입력과 처리

```python
def has_question_actor_reversal(approved_text: str, reply: str) -> bool:
```

주요 분기 조건은 `not source`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def has_question_actor_reversal(approved_text: str, reply: str) -> bool:
    """질문한 역할이 후보에서 질문받는 대상으로 바뀐 명시적 패턴을 탐지한다.

    예: '기자인데 ... 물었습니다' → '기자님에게 ... 질문을 했습니다'.
    한국어 전체를 해석하는 문법 분석기가 아니므로 이 패턴 밖은 의미 검증에 맡긴다.
    """
    source = re.search(r"(?:^|\s)([가-힣]{1,10})(?:인데|가|는)\s.*(?:물었|질문)", approved_text)
    if not source:
        return False
    actor = source.group(1)
    return bool(re.search(re.escape(actor) + r"(?:님|씨)?(?:에게|한테)\s[^.!?]*(?:질문[^.!?]*했|물었)", reply))
````

