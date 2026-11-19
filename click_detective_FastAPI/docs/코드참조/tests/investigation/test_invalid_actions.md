# `tests/investigation/test_invalid_actions.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/investigation/test_invalid_actions.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 67줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

investigation/test_invalid_actions.py의 회귀 동작을 확인한다.

## `test_unearned_sources_and_invalid_actions`

[소스 선언 위치](../../../../tests/investigation/test_invalid_actions.py#L6)

```python
def test_unearned_sources_and_invalid_actions(api, play):
    ...
```

수집하지 않은 출처·미래 단계·승인 사실 주입을 거절한다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
