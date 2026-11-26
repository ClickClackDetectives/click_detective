# `tests/dialogue/test_reply_availability.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/dialogue/test_reply_availability.py)

게임에서 전송한 유효 질문은 모델 실패·쟁점 여부와 무관하게 답변을 확정한다.

## `test_generation_failure_preserves_graph_retrieval`

[소스 선언](../../../../tests/dialogue/test_reply_availability.py#L17)

```python
def test_generation_failure_preserves_graph_retrieval(api, game, monkeypatch, vector_route):
    ...
```

검색을 완료했어도 생성 실패가 승인 사실의 전달로 기록되지 않는지 확인한다.

**인자**

- api: 심문 API 호출 함수.
- game: 새 수사 상태.
- monkeypatch: 생성 모델의 장애를 주입하는 도구.
- vector_route: 검색기와 생성 모델을 사용하도록 설정한 서비스.

**반환값**

- None: 검색을 실행한 뒤 중립 응답만 확정하는지 확인한다.

## `test_generation_failure_commits_neutral_reply_once`

[소스 선언](../../../../tests/dialogue/test_reply_availability.py#L54)

```python
def test_generation_failure_commits_neutral_reply_once(api, client, game, monkeypatch, failure):
    ...
```

모델 실패는 중립 응답으로 복구하며 같은 UUID를 중복 소비하지 않는다.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- client: HTTP 요청을 실행하는 클라이언트.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.
- failure: 테스트에서 재현할 실패 종류.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_failed_generated_admission_does_not_unlock_finding`

[소스 선언](../../../../tests/dialogue/test_reply_availability.py#L119)

```python
def test_failed_generated_admission_does_not_unlock_finding(api, client, play, monkeypatch):
    ...
```

중립 응답은 제시 조건을 통과한 쟁점도 공개하지 않는다.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- client: HTTP 요청을 실행하는 클라이언트.
- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_real_graph_rejection_returns_neutral`

[소스 선언](../../../../tests/dialogue/test_reply_availability.py#L173)

```python
async def test_real_graph_rejection_returns_neutral(client, monkeypatch):
    ...
```

출력 형식을 거절한 그래프는 중립 응답을 반환한다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_default_player_policy_enables_reply_recovery`

[소스 선언](../../../../tests/dialogue/test_reply_availability.py#L229)

```python
def test_default_player_policy_enables_reply_recovery():
    ...
```

신규 실행도 기본적으로 생성 오류를 플레이어에게 502로 내보내지 않는다.

**인자**

- 없음.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
