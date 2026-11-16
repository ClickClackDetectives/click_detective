# `tests/investigation/test_game_progress.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/investigation/test_game_progress.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 159줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

investigation/test_game_progress.py의 회귀 동작을 확인한다.

## 함께 읽을 코드

- [tests/investigation/data_helpers.py](data_helpers.md)

## `test_cache_revision_detail_and_notes`

[소스 선언 위치](../../../../tests/investigation/test_game_progress.py#L8)

```python
def test_cache_revision_detail_and_notes(api, play):
    ...
```

반복 열람·완료 재전송·UUID 충돌·오래된 revision·저장 복원을 검사한다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_full_game_to_100_percent_and_correct_verdict`

[소스 선언 위치](../../../../tests/investigation/test_game_progress.py#L65)

```python
def test_full_game_to_100_percent_and_correct_verdict(api, play):
    ...
```

데이터 29개·쟁점 10개·추론 10개를 실제 획득하고 정확한 고발로 종결한다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
