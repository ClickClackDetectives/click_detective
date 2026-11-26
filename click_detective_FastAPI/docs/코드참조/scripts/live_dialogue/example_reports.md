# `scripts/live_dialogue/example_reports.py`

[코드 참조 목차](../../README.md) · [스크립트 목차](../README.md) · [실제 소스](../../../../scripts/live_dialogue/example_reports.py)

130개 대화 사례의 JSON과 발표용 문서를 갱신한다.

## `save`

[소스 선언](../../../../scripts/live_dialogue/example_reports.py#L10)

```python
def save(tester, finished=False):
    ...
```

비밀값을 가리고 JSON과 읽기 쉬운 문서를 매 사례마다 원자적으로 갱신한다.

**인자**

- tester: 검사 사례와 HTTP 기록을 관리하는 실서버 테스트 객체.
- finished: 모든 실서버 검사 사례가 완료되었는지 여부.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
