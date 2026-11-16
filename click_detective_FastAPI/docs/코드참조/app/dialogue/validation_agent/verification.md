# `app/dialogue/validation_agent/verification.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/dialogue/validation_agent/verification.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 66줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

후보 대사가 승인 의미를 보존하는지 최종 판정한다.

## 함께 읽을 코드

- [app/dialogue/diagnostics.py](../diagnostics.md)
- [app/dialogue/reply_validation.py](../reply_validation.md)
- [app/dialogue/schemas.py](../schemas.md)
- [app/dialogue/state.py](../state.md)
- [app/dialogue/validation_agent/critical_facts.py](critical_facts.md)
- [app/dialogue/validation_agent/report_policy.py](report_policy.md)
- [app/dialogue/validation_agent/verification_reports.py](verification_reports.md)

## `SemanticVerifier`

[소스 선언 위치](../../../../../app/dialogue/validation_agent/verification.py#L12)

```python
class SemanticVerifier:
    ...
```

규칙 검사와 모델 보고서를 결합해 대사의 의미 보존을 판정한다.

**파라미터**

- settings: 모델 실행과 검색에 사용할 설정.
- model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

**반환값**

SemanticVerifier: 위 역할을 수행하도록 생성된 객체.

## `SemanticVerifier.__init__`

[소스 선언 위치](../../../../../app/dialogue/validation_agent/verification.py#L23)

```python
def __init__(self, settings, model):
    ...
```

사용할 의존성과 초기 상태를 준비한다.

**파라미터**

- settings: 모델 실행과 검색에 사용할 설정.
- model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `SemanticVerifier.verify`

[소스 선언 위치](../../../../../app/dialogue/validation_agent/verification.py#L35)

```python
async def verify(
    self, request: CharacterReplyRequest, response: CharacterReplyResponse
) -> CharacterReplyResponse:
    ...
```

별도 모델 호출의 의미 판정을 확인한다. 형식 재시도 후에도 불확실하면 거절한다.

**파라미터**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- response (CharacterReplyResponse): 검사하거나 저장할 최종 대사 응답.

**반환값**

CharacterReplyResponse: 의미 검증 결과로 사실 ID를 확정한 응답.
