# `tests/investigation/test_invalid_actions.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/investigation/test_invalid_actions.py)

investigation/test_invalid_actions.py의 회귀 동작을 확인한다.

## `test_unearned_sources_and_invalid_actions`

[소스 선언](../../../../tests/investigation/test_invalid_actions.py#L6)

```python
def test_unearned_sources_and_invalid_actions(api, play):
    ...
```

수집하지 않은 출처·미래 단계·승인 사실 주입을 거절한다.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
