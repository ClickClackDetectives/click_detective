# `app/dialogue/interrogation_graph.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/dialogue/interrogation_graph.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 142줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

전처리 → 생성 → 검증의 연결과 전체 실행 시간을 관리한다.

## 함께 읽을 코드

- [app/config.py](../config.md)
- [app/dialogue/diagnostics.py](diagnostics.md)
- [app/dialogue/inference_agent/agent.py](inference_agent/agent.md)
- [app/dialogue/local_model.py](local_model.md)
- [app/dialogue/preprocess_agent/agent.py](preprocess_agent/agent.md)
- [app/dialogue/schemas.py](schemas.md)
- [app/dialogue/state.py](state.md)
- [app/dialogue/validation_agent_v1/agent.py](validation_agent/agent.md)
- [app/dialogue/validation_agent_v1/evidence_checks.py](validation_agent/evidence_checks.md)

## `InterrogationGraph`

[소스 선언 위치](../../../../app/dialogue/interrogation_graph.py#L22)

```python
class InterrogationGraph:
    ...
```

전처리·생성·검증의 실행 순서와 전체 시간 제한을 관리한다.

**파라미터**

- settings (Settings): 모델 실행과 검색에 사용할 설정.
- model (ReplyModel): 대사 생성과 의미 검증에 사용할 모델 실행 객체.

**반환값**

InterrogationGraph: 위 역할을 수행하도록 생성된 객체.

## `InterrogationGraph.__init__`

[소스 선언 위치](../../../../app/dialogue/interrogation_graph.py#L33)

```python
def __init__(self, settings: Settings, model: ReplyModel) -> None:
    ...
```

한 모델을 생성·검증 호출에 공유한다. 검증자에게 생성자의 내부 추론은 전달하지 않는다.

**파라미터**

- settings (Settings): 모델 실행과 검색에 사용할 설정.
- model (ReplyModel): 대사 생성과 의미 검증에 사용할 모델 실행 객체.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `InterrogationGraph.next_step`

[소스 선언 위치](../../../../app/dialogue/interrogation_graph.py#L66)

```python
def next_step(state: InterrogationState) -> str:
    ...
```

검증이 요청한 경우에만 제한된 재생성을 수행한다.

**파라미터**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

**반환값**

str: 재생성이 필요하면 retry, 종료하면 done.

## `InterrogationGraph.preprocess_agent`

[소스 선언 위치](../../../../app/dialogue/interrogation_graph.py#L79)

```python
async def preprocess_agent(self, state: InterrogationState) -> dict:
    ...
```

전처리 에이전트에 승인 사실 정리와 프롬프트 구성을 맡긴다.

**파라미터**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

**반환값**

dict: 생성 프롬프트와 초기 생성 횟수.

## `InterrogationGraph.inference_agent`

[소스 선언 위치](../../../../app/dialogue/interrogation_graph.py#L90)

```python
async def inference_agent(self, state: InterrogationState) -> dict:
    ...
```

생성 에이전트에 후보 대사 작성을 맡긴다.

**파라미터**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

**반환값**

dict: 후보 대사와 시도 횟수 또는 실행 오류 상태.

## `InterrogationGraph.validation_agent`

[소스 선언 위치](../../../../app/dialogue/interrogation_graph.py#L101)

```python
async def validation_agent(self, state: InterrogationState) -> dict:
    ...
```

검증 에이전트에 후보 검사와 재생성 판단을 맡긴다.

**파라미터**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

**반환값**

dict: 최종 응답 또는 재생성 여부와 거절 코드.

## `InterrogationGraph.generate`

[소스 선언 위치](../../../../app/dialogue/interrogation_graph.py#L115)

```python
async def generate(self, request: CharacterReplyRequest) -> CharacterReplyResponse:
    ...
```

생성·검증·재시도를 모두 포함한 전체 제한 시간 안에서 그래프를 실행한다.

**파라미터**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.

**반환값**

CharacterReplyResponse: 검증을 통과하거나 승인 원문으로 복구한 최종 응답.
