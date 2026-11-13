# app/dialogue/semantic_verification.py 상세 설명

[문서 목차](../../../README.md) · [파일별 목차](../../README.md) · [현재 소스](../../../../app/dialogue/semantic_verification.py)

## 역할과 읽는 순서

모델이 인용문을 다시 쓰지 않고 후보 문장 번호를 선택하게 하는 의미 검증 계약.

아래 함수의 입력과 조건을 먼저 읽고 연결된 호출을 원본 소스에서 따라가세요.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## CandidateSentence

[원본 12번째 줄](../../../../app/dialogue/semantic_verification.py#L12)

서버가 원본 대사에서 잘라낸 문장. 번호가 원문의 실제 구간에 연결된다.

### 선언 필드

```python
id: int
start: int
end: int
text: str
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## candidate_sentences

[원본 21번째 줄](../../../../app/dialogue/semantic_verification.py#L21)

문장 번호와 원문 위치를 만든다. 원문을 교정하거나 바꿔 인용을 맞추지 않는다.

### 입력과 처리

```python
def candidate_sentences(reply: str) -> list[CandidateSentence]:
```

주요 분기 조건은 `left < right`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def candidate_sentences(reply: str) -> list[CandidateSentence]:
    """문장 번호와 원문 위치를 만든다. 원문을 교정하거나 바꿔 인용을 맞추지 않는다."""
    result = []
    start = 0
    boundaries = [match.end() for match in re.finditer(r"(?<=[.!?。！？])\s+|\n+", reply)] + [len(reply)]
    for end in boundaries:
        left = start
        while left < end and reply[left].isspace():
            left += 1
        right = end
        while right > left and reply[right - 1].isspace():
            right -= 1
        if left < right:
            result.append(CandidateSentence(len(result), left, right, reply[left:right]))
        start = end
    return result
````

## SemanticReport

[원본 39번째 줄](../../../../app/dialogue/semantic_verification.py#L39)

짧은 검증 출력. 각 checks 항목은 [검증항목 번호, 포함 여부, 후보문장 번호 목록].

### 선언 필드

```python
checks: list[tuple[StrictInt, StrictBool, list[StrictInt]]] = Field(max_length=256)
has_contradiction: StrictBool
has_unsupported_claims: StrictBool
history_consistent: StrictBool
persona_consistent: StrictBool
uncertain: StrictBool
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

