# `scripts/live_dialogue/case_runner.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../scripts/live_dialogue/case_runner.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 105줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

독립 수사의 생성, 심문과 저장 결과를 검사한다.

## 함께 읽을 코드

- [scripts/live_dialogue/errors.py](errors.md)

## `run_case`

[소스 선언 위치](../../../../scripts/live_dialogue/case_runner.py#L8)

```python
def run_case(tester, name, definition, catalog):
    ...
```

사례마다 독립 수사를 사용해 앞선 대사·질문 횟수의 영향을 줄인다.

**파라미터**

- tester: 검사 사례와 HTTP 기록을 관리하는 실서버 테스트 객체.
- name: 읽을 파일 또는 실행할 사례의 이름.
- definition: 질문, 준비 자료와 기대 결과를 담은 검사 사례.
- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
