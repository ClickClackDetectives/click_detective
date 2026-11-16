# `tests/dialogue/test_paraphrase_generation.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/dialogue/test_paraphrase_generation.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 204줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

실제 사건 승인 데이터로 재서술 허용·호출별 디코딩·사실 변조 거절을 검사한다.

모의 검증 판정은 그래프 계약을 확인하기 위한 것이며 실제 Qwen 품질 측정은 아니다.

## 함께 읽을 코드

- [app/config.py](../../app/config.md)
- [app/dialogue/critical_facts.py](../../app/dialogue/critical_facts.md)
- [app/dialogue/interrogation_graph.py](../../app/dialogue/interrogation_graph.md)
- [app/dialogue/local_model.py](../../app/dialogue/local_model.md)
- [app/dialogue/prompting.py](../../app/dialogue/prompting.md)
- [app/schemas.py](../../app/schemas.md)

## `make_request`

[소스 선언 위치](../../../../tests/dialogue/test_paraphrase_generation.py#L20)

```python
def make_request(client):
    ...
```

프로젝트의 윤재혁 소개 원문을 실제 승인 계획으로 가져온다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

CharacterReplyRequest: 현재 사건의 승인 계획으로 구성한 테스트 요청.

## `test_generation_samples_but_verification_does_not`

[소스 선언 위치](../../../../tests/dialogue/test_paraphrase_generation.py#L42)

```python
def test_generation_samples_but_verification_does_not():
    ...
```

동일 모델이어도 생성 자유도가 검증 JSON 호출에 전달되지 않아야 한다.

**파라미터**

- 없음.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_sampling_settings_reject_invalid_values`

[소스 선언 위치](../../../../tests/dialogue/test_paraphrase_generation.py#L81)

```python
def test_sampling_settings_reject_invalid_values(field, value):
    ...
```

잘못된 설정을 GPU 실행 전에 거절한다.

**파라미터**

- field: 검사할 설정 필드 이름.
- value: 검사·변환하거나 비밀값을 가릴 입력 값.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_nonverbatim_reply_passes_graph_with_semantic_evidence`

[소스 선언 위치](../../../../tests/dialogue/test_paraphrase_generation.py#L95)

```python
async def test_nonverbatim_reply_passes_graph_with_semantic_evidence(client):
    ...
```

원문 부분 문자열이 없어도 별도 의미 판정과 규칙 검사를 통과하면 stop으로 반환한다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_nonverbatim_reply_passes_graph_with_semantic_evidence.ParaphraseModel`

[소스 선언 위치](../../../../tests/dialogue/test_paraphrase_generation.py#L108)

```python
class ParaphraseModel:
    ...
```

두 승인 문장의 의미가 두 후보 문장에 있다는 판정을 명시적으로 제공한다.

**파라미터**

- 없음.

**반환값**

ParaphraseModel: 위 역할을 수행하도록 생성된 객체.

## `test_nonverbatim_reply_passes_graph_with_semantic_evidence.ParaphraseModel.__init__`

[소스 선언 위치](../../../../tests/dialogue/test_paraphrase_generation.py#L120)

```python
def __init__(self):
    ...
```

사용할 의존성과 초기 상태를 준비한다.

**파라미터**

- 없음.

**반환값**

None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.

## `test_nonverbatim_reply_passes_graph_with_semantic_evidence.ParaphraseModel.generate`

[소스 선언 위치](../../../../tests/dialogue/test_paraphrase_generation.py#L131)

```python
async def generate(self, messages, *, purpose="dialogue"):
    ...
```

호출 목적을 기록하여 생성과 검증의 디코딩 분리 연결을 검사한다.

**파라미터**

- messages: 모델에 전달할 역할별 프롬프트 목록.
- purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

**반환값**

str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `test_style_freedom_does_not_authorize_new_quantities`

[소스 선언 위치](../../../../tests/dialogue/test_paraphrase_generation.py#L167)

```python
def test_style_freedom_does_not_authorize_new_quantities(client):
    ...
```

재서술을 허용해도 승인되지 않은 사건 금액을 추가할 권한은 없다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_prompts_preserve_facts_but_allow_rewording`

[소스 선언 위치](../../../../tests/dialogue/test_paraphrase_generation.py#L185)

```python
def test_prompts_preserve_facts_but_allow_rewording(client):
    ...
```

생성에는 재서술 지침을, 검증에는 의미 동등 표현 허용 지침을 전달한다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
