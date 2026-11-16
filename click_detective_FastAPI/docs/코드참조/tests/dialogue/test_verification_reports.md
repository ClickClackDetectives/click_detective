# `tests/dialogue/test_verification_reports.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/dialogue/test_verification_reports.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 184줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

검증 책임 분리 후에도 배치·보고서 재요청·의미상 거절 정책을 유지한다.

## 함께 읽을 코드

- [app/dialogue/interrogation_graph.py](../../app/dialogue/interrogation_graph.md)
- [app/investigation/schemas.py](../../app/investigation/schemas.md)
- [tests/dialogue/models.py](models.md)

## `ReportErrorModel`

[소스 선언 위치](../../../../tests/dialogue/test_verification_reports.py#L15)

```python
class ReportErrorModel(ApprovedModel):
    ...
```

정상 모델 응답 일부를 바꾸어 보고서 오류를 재현한다.

**파라미터**

- error_kind: json, schema, missing, evidence 또는 semantic 오류 종류.
- bad_reports: 처음 몇 번의 검증 보고서를 잘못 반환할지 지정하는 수.

**반환값**

ReportErrorModel: 검증 요청을 관찰하고 지정한 오류를 만드는 모의 모델.

## `ReportErrorModel.__init__`

[소스 선언 위치](../../../../tests/dialogue/test_verification_reports.py#L26)

```python
def __init__(self, error_kind, bad_reports=1):
    ...
```

오류 주입 조건과 검증 호출 기록을 준비한다.

**파라미터**

- error_kind: 검증 응답에 주입할 오류 종류.
- bad_reports: 잘못된 검증 응답을 반환할 횟수.

**반환값**

None: 내부 호출 기록과 오류 조건을 초기화한다.

## `ReportErrorModel.generate`

[소스 선언 위치](../../../../tests/dialogue/test_verification_reports.py#L42)

```python
async def generate(self, messages, *, purpose="dialogue"):
    ...
```

생성은 승인 원문을 사용하고 검증 응답에만 지정한 오류를 주입한다.

**파라미터**

- messages: 생성 또는 검증용 프롬프트.
- purpose: dialogue 또는 verification 호출 목적.

**반환값**

str: 정상 생성 원문 또는 오류가 주입된 검증 보고서 문자열.

## `profile_request`

[소스 선언 위치](../../../../tests/dialogue/test_verification_reports.py#L73)

```python
def profile_request(client):
    ...
```

두 문장으로 구성된 실제 인물 소개를 승인 요청으로 만든다.

**파라미터**

- client: fixture 모드로 실행한 FastAPI 테스트 클라이언트.

**반환값**

CharacterReplyRequest: 윤재혁 소개의 두 문장을 필수로 포함하는 요청.

## `test_report_format_retry_keeps_same_candidate`

[소스 선언 위치](../../../../tests/dialogue/test_verification_reports.py#L96)

```python
async def test_report_format_retry_keeps_same_candidate(client, error_kind):
    ...
```

보고서 오류만 재요청하고 후보 대사를 새로 생성하지 않는지 확인한다.

**파라미터**

- client: 테스트 앱과 실행 설정을 제공하는 클라이언트.
- error_kind: 처음 보고서에 주입할 형식 또는 근거 오류 종류.

**반환값**

None: 같은 후보로 검증 두 번, 대사 생성 한 번인지 검사한다.

## `test_report_format_exhaustion_does_not_regenerate`

[소스 선언 위치](../../../../tests/dialogue/test_verification_reports.py#L121)

```python
async def test_report_format_exhaustion_does_not_regenerate(client):
    ...
```

보고서 형식 오류의 상한을 소진하면 대사 재생성 없이 오류로 끝낸다.

**파라미터**

- client: 복구가 비활성화된 fixture 앱 클라이언트.

**반환값**

None: HTTP 502와 검증 오류 코드, 생성 한 번을 확인한다.

## `test_semantic_rejection_regenerates_instead_of_retrying_report`

[소스 선언 위치](../../../../tests/dialogue/test_verification_reports.py#L140)

```python
async def test_semantic_rejection_regenerates_instead_of_retrying_report(client):
    ...
```

의미상 거절은 검사표 재요청이 아닌 대사 재생성으로 처리한다.

**파라미터**

- client: 두 번의 대사 생성을 허용하는 테스트 앱 클라이언트.

**반환값**

None: 생성과 검증이 각각 두 번이며 같은 후보 재검사 지시가 없는지 확인한다.

## `test_batches_keep_entire_approval_context`

[소스 선언 위치](../../../../tests/dialogue/test_verification_reports.py#L162)

```python
async def test_batches_keep_entire_approval_context(client):
    ...
```

검사 항목을 나누어도 모든 배치에 원래 승인 계획을 유지한다.

**파라미터**

- client: 기본 설정을 제공하는 테스트 앱 클라이언트.

**반환값**

None: 두 문장을 나누어 검증해도 원래 사실 ID 전체가 확인되는지 검사한다.
