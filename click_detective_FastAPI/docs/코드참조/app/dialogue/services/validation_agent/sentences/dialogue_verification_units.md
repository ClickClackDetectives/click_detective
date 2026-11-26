# `app/dialogue/services/validation_agent/sentences/dialogue_verification_units.py`

[코드 참조 목차](../../../../../README.md) · [도메인 목차](../../../README.md) · [실제 소스](../../../../../../../app/dialogue/services/validation_agent/sentences/dialogue_verification_units.py)

복합 승인 사실을 문장별 검증 항목으로 나눈다. 공개 권한과 원래 사실 ID는 바꾸지 않는다.

## `VerificationUnit`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/sentences/dialogue_verification_units.py#L10)

```python
class VerificationUnit:
    ...
```

한 문장의 검증 ID와 원래 사실 ID. 일부 문장만 통과한 사실은 전체 통과가 아니다.

**인자**

- id (str): 항목을 구분하는 식별자.
- fact_id (str): 원래 승인 사실의 식별자.
- text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

**반환값**

- VerificationUnit: 위 역할을 수행하도록 생성된 객체.

## `build_verification_units`

[소스 선언](../../../../../../../app/dialogue/services/validation_agent/sentences/dialogue_verification_units.py#L27)

```python
def build_verification_units(request: CharacterReplyRequest) -> list[VerificationUnit]:
    ...
```

문장 종결 부호 뒤의 공백·줄바꿈만 구분한다. 조사·부정·문장 내부 절은 자르지 않는다.

이는 완전한 의미 원자화가 아니다. 한 문장 안의 행위자·시각·부정까지 확인하는
책임은 의미 검증에 남는다. 원문 순서와 모든 텍스트 조각을 보존한다.

**인자**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.

**반환값**

- list[VerificationUnit]: 원래 사실 ID를 유지한 문장별 검증 항목.
