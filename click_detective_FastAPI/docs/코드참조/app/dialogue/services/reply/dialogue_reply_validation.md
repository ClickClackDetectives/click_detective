# `app/dialogue/services/reply/dialogue_reply_validation.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/dialogue/services/reply/dialogue_reply_validation.py)

응답 검증과 고정 대사 조립. HTTP·로컬 모델이 공통으로 사용한다.

## `validate_generation`

[소스 선언](../../../../../../app/dialogue/services/reply/dialogue_reply_validation.py#L11)

```python
def validate_generation(request: CharacterReplyRequest, response: CharacterReplyResponse, *, require_verbatim: bool=True, require_all_facts: bool=True) -> None:
    ...
```

식별 정보·사실 ID·필수 사실을 검사한다. 고정 모드는 원문까지 대조한다. 실패하면 ValueError를 낸다.

require_verbatim=False는 의미 검증을 별도로 수행하는 local 그래프에서만 사용한다.
ID 검사만으로 내용이 참이라고 보장하지 않는다.
이 검사는 임의의 추가 문장이 참인지 판별하지는 않는다. 그 범위는 조립 단계에서
승인 원문만 사용하도록 제한한다.

**인자**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- response (CharacterReplyResponse): 검사하거나 저장할 최종 대사 응답.
- require_verbatim (bool): 응답에 승인 원문이 그대로 들어 있는지 검사할지 여부.
- require_all_facts (bool): 모든 필수 사실 ID의 포함을 강제할지 여부.

**반환값**

- None: 반환값 없음.

## `assemble_reply`

[소스 선언](../../../../../../app/dialogue/services/reply/dialogue_reply_validation.py#L62)

```python
def assemble_reply(request: CharacterReplyRequest) -> str:
    ...
```

모든 승인 사실을 순서대로 붙인다. 사실이 없으면 중립 대사를 준다.

**인자**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.

**반환값**

- str: 승인 원문을 순서대로 연결한 대사. 사실이 없으면 중립 대사.
