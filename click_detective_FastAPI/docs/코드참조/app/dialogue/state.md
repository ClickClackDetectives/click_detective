# `app/dialogue/state.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/dialogue/state.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 83줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

대화 생성 과정에서 주고받는 상태와 오류 형식을 정의한다.

## 함께 읽을 코드

- [app/dialogue/schemas.py](schemas.md)

## `GeneratedReply`

[소스 선언 위치](../../../../app/dialogue/state.py#L17)

```python
class GeneratedReply(DTO):
    ...
```

모델이 직접 작성한 대사. 선택적 ID 자기 신고는 허용 범위만 검사하며 별도 검증한다.

**파라미터**

- reply (ReplyText): 의미를 검사하거나 문장으로 나눌 후보 대사.
- used_fact_ids (list[Identifier]): 응답에서 사용한 사실 식별자 목록.

**반환값**

GeneratedReply: 위 역할을 수행하도록 생성된 객체.

## `OutputRejected`

[소스 선언 위치](../../../../app/dialogue/state.py#L32)

```python
class OutputRejected(ValueError):
    ...
```

고정 오류 코드와 안전한 하위 사유. 모델 원문·프롬프트는 담지 않는다.

**파라미터**

- code (str): 원문을 포함하지 않는 고정 오류 코드.
- detail (str): 오류를 구분하기 위한 추가 사유. 비밀값은 포함하지 않는다.

**반환값**

OutputRejected: 위 역할을 수행하도록 생성된 객체.

## `OutputRejected.__init__`

[소스 선언 위치](../../../../app/dialogue/state.py#L43)

```python
def __init__(self, code: str, detail: str = "") -> None:
    ...
```

HTTP 코드는 유지하고 내부 형식 실패 원인을 별도로 추적한다.

**파라미터**

- code (str): 원문을 포함하지 않는 고정 오류 코드.
- detail (str): 오류를 구분하기 위한 추가 사유. 비밀값은 포함하지 않는다.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `InterrogationState`

[소스 선언 위치](../../../../app/dialogue/state.py#L57)

```python
class InterrogationState(TypedDict, total=False):
    ...
```

요청별 지역 상태. 원본 생성·검증 내용은 DB나 GameState에 저장하지 않는다.

**파라미터**

- request (CharacterReplyRequest): 승인 사실과 필수 사실 ID를 포함한 대화 요청.
- messages (list[dict[str, str]]): 모델에 전달할 역할별 프롬프트 목록.
- raw_output (str): 모델이 생성한 원문 대사.
- attempt (int): 대사를 생성한 누적 횟수.
- error_status (int | None): 모델 실행 실패의 HTTP 상태 코드.
- retry (bool): 새 대사 생성을 요청할지 여부.
- rejection_code (str): 이전 후보가 거절된 오류 코드.
- response (CharacterReplyResponse): 검사하거나 저장할 최종 대사 응답.

**반환값**

InterrogationState: 위 역할을 수행하도록 생성된 객체.
