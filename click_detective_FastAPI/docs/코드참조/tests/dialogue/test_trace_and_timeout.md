# `tests/dialogue/test_trace_and_timeout.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/dialogue/test_trace_and_timeout.py)

live_dialogue/test_trace_and_timeout.py의 회귀 동작을 확인한다.

## `test_live_runner_requires_matching_local_trace_and_nf4`

[소스 선언](../../../../tests/dialogue/test_trace_and_timeout.py#L16)

```python
def test_live_runner_requires_matching_local_trace_and_nf4(client, monkeypatch, tmp_path, preprocess_stage):
    ...
```

버전 이름만으로 NF4를 확정하지 않고 해당 요청의 실행 진단을 요구한다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.
- tmp_path: pytest가 제공하는 테스트별 임시 디렉터리.
- preprocess_stage: 새 진단과 기존 진단에서 사용하는 전처리 단계 이름.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_live_runner_timeout_preserves_uuid_without_automatic_retry`

[소스 선언](../../../../tests/dialogue/test_trace_and_timeout.py#L74)

```python
def test_live_runner_timeout_preserves_uuid_without_automatic_retry(client):
    ...
```

시간 초과의 모호한 결과를 성공으로 바꾸거나 새 UUID로 몰래 재전송하지 않는다.

**인자**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
