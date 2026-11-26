# `tests/dialogue/inference_agent/test_paraphrase_generation.py`

[코드 참조 목차](../../../README.md) · [테스트 목차](../../README.md) · [실제 소스](../../../../../tests/dialogue/inference_agent/test_paraphrase_generation.py)

실제 사건 승인 데이터로 재서술 허용·호출별 디코딩·사실 변조 거절을 검사한다.

모의 검증 판정은 그래프 계약을 확인하기 위한 것이며 실제 Qwen 품질 측정은 아니다.

## `make_request`

[소스 선언](../../../../../tests/dialogue/inference_agent/test_paraphrase_generation.py#L24)

```python
def make_request(client):
    ...
```

프로젝트의 윤재혁 소개 원문을 실제 승인 계획으로 가져온다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

- CharacterReplyRequest: 현재 사건의 승인 계획으로 구성한 테스트 요청.

## `test_generation_samples_but_verification_does_not`

[소스 선언](../../../../../tests/dialogue/inference_agent/test_paraphrase_generation.py#L46)

```python
def test_generation_samples_but_verification_does_not():
    ...
```

동일 모델이어도 생성 자유도가 검증 JSON 호출에 전달되지 않아야 한다.

**인자**

- 없음.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_sampling_settings_reject_invalid_values`

[소스 선언](../../../../../tests/dialogue/inference_agent/test_paraphrase_generation.py#L85)

```python
def test_sampling_settings_reject_invalid_values(field, value):
    ...
```

잘못된 설정을 GPU 실행 전에 거절한다.

**인자**

- field: 검사할 설정 필드 이름.
- value: 검사·변환하거나 비밀값을 가릴 입력 값.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_nonverbatim_reply_passes_graph_with_semantic_evidence`

[소스 선언](../../../../../tests/dialogue/inference_agent/test_paraphrase_generation.py#L99)

```python
async def test_nonverbatim_reply_passes_graph_with_semantic_evidence(client):
    ...
```

원문 부분 문자열이 없어도 별도 의미 판정과 규칙 검사를 통과하면 stop으로 반환한다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_style_freedom_does_not_authorize_new_quantities`

[소스 선언](../../../../../tests/dialogue/inference_agent/test_paraphrase_generation.py#L162)

```python
def test_style_freedom_does_not_authorize_new_quantities(client):
    ...
```

재서술을 허용해도 승인되지 않은 사건 금액을 추가할 권한은 없다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_prompts_preserve_facts_but_allow_rewording`

[소스 선언](../../../../../tests/dialogue/inference_agent/test_paraphrase_generation.py#L180)

```python
def test_prompts_preserve_facts_but_allow_rewording(client):
    ...
```

생성에는 재서술 지침을, 검증에는 의미 동등 표현 허용 지침을 전달한다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_character_speech_style_reaches_generation_prompt`

[소스 선언](../../../../../tests/dialogue/inference_agent/test_paraphrase_generation.py#L202)

```python
def test_character_speech_style_reaches_generation_prompt(client, monkeypatch, style):
    ...
```

인물 지침이 생성에 전달되고 미작성 상태에서는 공통 지침이 적용된다.

**인자**

- client: 실제 사건 카탈로그를 읽은 FastAPI 테스트 클라이언트.
- monkeypatch: 카탈로그를 테스트 중에만 수정하는 도구.
- style: 인물에게 설정할 문구 또는 필드 미설정을 나타내는 None.
**반환값**

- None: 생성과 검증의 페르소나에 설정한 문구가 반영됐는지 확인한다.
