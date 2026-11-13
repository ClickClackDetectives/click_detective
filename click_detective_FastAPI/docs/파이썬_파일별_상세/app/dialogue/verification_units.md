# app/dialogue/verification_units.py 상세 설명

[문서 목차](../../../README.md) · [파일별 목차](../../README.md) · [현재 소스](../../../../app/dialogue/verification_units.py)

## 역할과 읽는 순서

복합 승인 사실을 문장별 검증 항목으로 나눈다. 공개 권한과 원래 사실 ID는 바꾸지 않는다.

아래 함수의 입력과 조건을 먼저 읽고 연결된 호출을 원본 소스에서 따라가세요.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## VerificationUnit

[원본 10번째 줄](../../../../app/dialogue/verification_units.py#L10)

한 문장의 검증 ID와 원래 사실 ID. 일부 문장만 통과한 사실은 전체 통과가 아니다.

### 선언 필드

```python
id: str
fact_id: str
text: str
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## build_verification_units

[원본 18번째 줄](../../../../app/dialogue/verification_units.py#L18)

문장 종결 부호 뒤의 공백·줄바꿈만 구분한다. 조사·부정·문장 내부 절은 자르지 않는다.

이는 완전한 의미 원자화가 아니다. 한 문장 안의 행위자·시각·부정까지 확인하는
책임은 의미 검증에 남는다. 원문 순서와 모든 텍스트 조각을 보존한다.

### 입력과 처리

```python
def build_verification_units(request: CharacterReplyRequest) -> list[VerificationUnit]:
```

### 실제 코드

````python
def build_verification_units(request: CharacterReplyRequest) -> list[VerificationUnit]:
    """문장 종결 부호 뒤의 공백·줄바꿈만 구분한다. 조사·부정·문장 내부 절은 자르지 않는다.

    이는 완전한 의미 원자화가 아니다. 한 문장 안의 행위자·시각·부정까지 확인하는
    책임은 의미 검증에 남는다. 원문 순서와 모든 텍스트 조각을 보존한다.
    """
    units = []
    for fact in request.allowed_facts:
        sentences = [text.strip() for text in re.split(r"(?<=[.!?。！？])\s+|\n+", fact.text) if text.strip()]
        for sentence in sentences:
            units.append(VerificationUnit(id=f"unit-{len(units)}", fact_id=fact.id, text=sentence))
    return units
````

