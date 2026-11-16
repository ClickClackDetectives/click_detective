# `app/dialogue/agents.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/dialogue/agents.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 51줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

이전 DialogueAgents 이름을 사용하는 코드를 위한 연결이다.

## 함께 읽을 코드

- [app/dialogue/inference_agent/agent.py](inference_agent/agent.md)
- [app/dialogue/preprocess_agent/agent.py](preprocess_agent/agent.md)

## `DialogueAgents`

[소스 선언 위치](../../../../app/dialogue/agents.py#L7)

```python
class DialogueAgents:
    ...
```

전처리와 생성 담당자에게 요청을 전달한다.

**파라미터**

- settings: 전처리와 생성 설정.
- model: 생성에 사용할 모델.

**반환값**

DialogueAgents: 기존 호출 이름을 제공하는 객체.

## `DialogueAgents.__init__`

[소스 선언 위치](../../../../app/dialogue/agents.py#L18)

```python
def __init__(self, settings, model):
    ...
```

두 단계의 담당자를 준비한다.

**파라미터**

- settings: 전처리와 생성 설정.
- model: 생성에 사용할 모델.

**반환값**

None: 담당 객체를 보관한다.

## `DialogueAgents.preprocess_agent`

[소스 선언 위치](../../../../app/dialogue/agents.py#L31)

```python
async def preprocess_agent(self, state):
    ...
```

전처리 담당자에게 현재 작업을 전달한다.

**파라미터**

- state: 현재 요청의 작업 상태.

**반환값**

dict: 생성에 사용할 자료와 초기 시도 횟수.

## `DialogueAgents.inference_agent`

[소스 선언 위치](../../../../app/dialogue/agents.py#L42)

```python
async def inference_agent(self, state):
    ...
```

생성 담당자에게 현재 작업을 전달한다.

**파라미터**

- state: 현재 요청의 작업 상태.

**반환값**

dict: 후보 대사 또는 실행 오류 상태.
