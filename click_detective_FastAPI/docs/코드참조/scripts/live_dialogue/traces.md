# `scripts/live_dialogue/traces.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../scripts/live_dialogue/traces.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 79줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

서버의 대화 생성 진단을 실서버 검사 보고서에 연결한다.

## `attach_traces`

[소스 선언 위치](../../../../scripts/live_dialogue/traces.py#L6)

```python
def attach_traces(report, trace_path, required=False):
    ...
```

같은 서버의 진단 JSONL을 선택적으로 읽어 요청별 3단계 호출 증거를 연결한다.

**파라미터**

- report: 검사 결과와 실행 기록을 담은 보고서.
- trace_path: 같은 서버가 기록한 진단 JSONL 파일 경로.
- required: 실행 진단 확인을 검사 통과의 필수 조건으로 적용할지 여부.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
