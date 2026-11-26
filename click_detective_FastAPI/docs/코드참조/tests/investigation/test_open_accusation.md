# `tests/investigation/test_open_accusation.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/investigation/test_open_accusation.py)

실제 사건 데이터로 초기·소수 근거 고발과 부족한 입증의 채점을 검사한다.

## `selections`

[소스 선언](../../../../tests/investigation/test_open_accusation.py#L11)

```python
def selections():
    ...
```

테스트만 서버 비공개 정답을 읽어 선택 채점과 근거 채점을 분리한다.

**인자**

- 없음.

**반환값**

- 테스트만 서버 비공개 정답을 읽어 선택 채점과 근거 채점을 분리한다.

## `test_initial_game_can_accuse_without_evidence`

[소스 선언](../../../../tests/investigation/test_open_accusation.py#L31)

```python
def test_initial_game_can_accuse_without_evidence(api, game, include_empty_evidence):
    ...
```

1차 조사·쟁점 0·추론 0이어도 제출하고, 입증 부족은 채점으로 처리한다.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.
- include_empty_evidence: 모의 보고서에 잘못된 빈 근거를 포함할지 여부.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_single_earned_inference_can_be_submitted`

[소스 선언](../../../../tests/investigation/test_open_accusation.py#L74)

```python
def test_single_earned_inference_can_be_submitted(play):
    ...
```

실제 1차 추론 하나만 확보해 제출해도 최소 5개 제한에 막히지 않는다.

**인자**

- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_unearned_inference_still_rejected_without_consuming_state`

[소스 선언](../../../../tests/investigation/test_open_accusation.py#L101)

```python
def test_unearned_inference_still_rejected_without_consuming_state(api, game):
    ...
```

제출 자유가 존재하지 않는 추론을 근거로 제출할 권한까지 주지는 않는다.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
