# `app/dialogue/controllers/dialogue_agent_test_controller.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/dialogue/controllers/dialogue_agent_test_controller.py)

실제 모델을 사용하는 내부 에이전트 검사 API.

## `agent_test_service`

[소스 선언](../../../../../app/dialogue/controllers/dialogue_agent_test_controller.py#L15)

```python
def agent_test_service(request: Request):
    ...
```

검사 API 활성화 여부와 로컬 그래프를 확인한다.

**인자**

- request: 실행 중인 앱에 접근할 HTTP 요청.

**반환값**

- ReplyService: 검사에 사용할 설정과 그래프를 보관한 서비스.

## `agent_test_config`

[소스 선언](../../../../../app/dialogue/controllers/dialogue_agent_test_controller.py#L33)

```python
async def agent_test_config(request: Request):
    ...
```

배치 전에 실제 서버의 진단 설정을 확인한다.

**인자**

- request: 실행 중인 앱에 접근할 HTTP 요청.

**반환값**

- dict: 진단 활성화 여부.

## `run_agent_test`

[소스 선언](../../../../../app/dialogue/controllers/dialogue_agent_test_controller.py#L49)

```python
async def run_agent_test(command: CharacterReplyRequest, request: Request) -> CharacterReplyResponse:
    ...
```

테스트 문맥으로 서버에 로드된 대화 그래프를 직접 실행한다.

**인자**

- command: 테스트용으로 제공한 승인 사실과 대화 문맥.
- request: 실행 중인 서버의 설정과 그래프에 접근할 HTTP 요청.

**반환값**

- CharacterReplyResponse: 세 에이전트가 처리한 최종 대화 응답.
