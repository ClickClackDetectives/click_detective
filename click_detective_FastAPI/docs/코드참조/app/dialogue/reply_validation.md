# `app/dialogue/reply_validation.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/dialogue/reply_validation.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 71줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

응답 검증과 고정 대사 조립. HTTP·로컬 모델이 공통으로 사용한다.

## 함께 읽을 코드

- [app/dialogue/schemas.py](schemas.md)

## `validate_generation`

[소스 선언 위치](../../../../app/dialogue/reply_validation.py#L9)

```python
def validate_generation(
    request: CharacterReplyRequest,
    response: CharacterReplyResponse,
    *,
    require_verbatim: bool = True,
) -> None:
    ...
```

식별 정보·사실 ID·필수 사실을 검사한다. 고정 모드는 원문까지 대조한다. 실패하면 ValueError를 낸다.

require_verbatim=False는 의미 검증을 별도로 수행하는 local 그래프에서만 사용한다.
ID 검사만으로 내용이 참이라고 보장하지 않는다.
이 검사는 임의의 추가 문장이 참인지 판별하지는 않는다. 그 범위는 조립 단계에서
승인 원문만 사용하도록 제한한다.

**파라미터**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- response (CharacterReplyResponse): 검사하거나 저장할 최종 대사 응답.
- require_verbatim (bool): 응답에 승인 원문이 그대로 들어 있는지 검사할지 여부.

**반환값**

None: 반환값 없음.

## `assemble_reply`

[소스 선언 위치](../../../../app/dialogue/reply_validation.py#L58)

```python
def assemble_reply(request: CharacterReplyRequest) -> str:
    ...
```

모든 승인 사실을 순서대로 붙인다. 사실이 없으면 중립 대사를 준다.

**파라미터**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.

**반환값**

str: 승인 원문을 순서대로 연결한 대사. 사실이 없으면 중립 대사.
