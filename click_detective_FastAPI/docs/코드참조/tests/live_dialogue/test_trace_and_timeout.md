# `tests/dialogue/test_trace_and_timeout.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/dialogue/test_trace_and_timeout.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 98줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

live_dialogue/test_trace_and_timeout.py의 회귀 동작을 확인한다.

## 함께 읽을 코드

- [app/config.py](../../app/config.md)
- [scripts/test_llm_api_live.py](../../scripts/test_llm_api_live.md)
- [tests/conftest.py](../conftest.md)
- [tests/dialogue/test_runner.py](test_runner.md)

## `test_live_runner_requires_matching_local_trace_and_nf4`

[소스 선언 위치](../../../../tests/dialogue/test_trace_and_timeout.py#L14)

```python
def test_live_runner_requires_matching_local_trace_and_nf4(
    client, monkeypatch, tmp_path
):
    ...
```

버전 이름만으로 NF4를 확정하지 않고 해당 요청의 실행 진단을 요구한다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.
- monkeypatch: 설정이나 의존성을 일시 교체하는 pytest 도구.
- tmp_path: pytest가 제공하는 테스트별 임시 디렉터리.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_live_runner_timeout_preserves_uuid_without_automatic_retry`

[소스 선언 위치](../../../../tests/dialogue/test_trace_and_timeout.py#L55)

```python
def test_live_runner_timeout_preserves_uuid_without_automatic_retry(client):
    ...
```

시간 초과의 모호한 결과를 성공으로 바꾸거나 새 UUID로 몰래 재전송하지 않는다.

**파라미터**

- client: HTTP 요청을 실행하는 클라이언트.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_live_runner_timeout_preserves_uuid_without_automatic_retry.send`

[소스 선언 위치](../../../../tests/dialogue/test_trace_and_timeout.py#L66)

```python
def send(request):
    ...
```

실서버 검사기의 요청을 테스트 클라이언트로 전달한다.

**파라미터**

- request: HTTP 요청 또는 승인 사실을 담은 대화 요청. 선언된 타입과 호출 위치에 따른다.

**반환값**

httpx.Response: 테스트 앱의 상태 코드·헤더·본문을 옮긴 HTTP 응답.
