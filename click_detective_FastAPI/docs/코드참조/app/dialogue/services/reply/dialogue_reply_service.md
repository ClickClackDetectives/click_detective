# `app/dialogue/services/reply/dialogue_reply_service.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/dialogue/services/reply/dialogue_reply_service.py)

정상 심문 대사를 생성하고 검증 실패 시 복구 정책을 적용한다.

## `ReplyService`

[소스 선언](../../../../../../app/dialogue/services/reply/dialogue_reply_service.py#L11)

```python
class ReplyService:
    ...
```

대화 그래프를 실행하고 일반 심문의 검증·복구를 담당한다.

**인자**

- settings: 대화 검증과 실패 복구 정책을 담은 설정.
- graph: 검색·생성·검증을 수행하는 대화 그래프.
- search_free: 자유 질문의 진술 검색을 사용할 수 있는지 여부.

**반환값**

- ReplyService: 일반 심문과 내부 검사에 사용할 대화 서비스.

## `ReplyService.__init__`

[소스 선언](../../../../../../app/dialogue/services/reply/dialogue_reply_service.py#L23)

```python
def __init__(self, settings, graph, *, search_free=False):
    ...
```

기동 시 준비한 대화 설정과 그래프를 보관한다.

**인자**

- settings: 대화 검증과 실패 복구를 설정하는 값.
- graph: 승인 문맥으로 대사를 생성하는 그래프.
- search_free: 자유 질문의 진술 검색을 사용할 수 있는지 여부.

**반환값**

- None: 반환값 없음.

## `ReplyService.reply`

[소스 선언](../../../../../../app/dialogue/services/reply/dialogue_reply_service.py#L38)

```python
async def reply(self, request, search_turn=None):
    ...
```

쟁점 유무와 무관하게 대사를 준비하고 실행 예외는 설정에 따라 중립 응답으로 복구한다.

**인자**

- request: 승인 사실을 담은 대화 요청.
- search_turn: 첫 노드에서 확정할 자유 질문의 승인 계획 또는 None.

**반환값**

- CharacterReplyResponse: 검증된 대사 또는 중립 응답.
