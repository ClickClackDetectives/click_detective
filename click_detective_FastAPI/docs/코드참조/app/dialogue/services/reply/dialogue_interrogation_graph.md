# `app/dialogue/services/reply/dialogue_interrogation_graph.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/dialogue/services/reply/dialogue_interrogation_graph.py)

전처리 → 생성 → 검증의 연결과 전체 실행 시간을 관리한다.

## `InterrogationGraph`

[소스 선언](../../../../../../app/dialogue/services/reply/dialogue_interrogation_graph.py#L34)

```python
class InterrogationGraph:
    ...
```

전처리·생성·검증의 실행 순서와 전체 시간 제한을 관리한다.

**인자**

- settings (Settings): 모델 실행과 검색에 사용할 설정.
- model (ReplyModel | None): 대사 생성과 검증에 사용할 모델. fixture에서는 None.
- question_search: 첫 노드에서 공개 진술을 찾는 검색기 또는 None.

**반환값**

- InterrogationGraph: 위 역할을 수행하도록 생성된 객체.

## `InterrogationGraph.__init__`

[소스 선언](../../../../../../app/dialogue/services/reply/dialogue_interrogation_graph.py#L46)

```python
def __init__(self, settings: Settings, model: ReplyModel | None, question_search=None) -> None:
    ...
```

한 모델을 생성·검증 호출에 공유한다. 검증자에게 생성자의 내부 추론은 전달하지 않는다.

**인자**

- settings (Settings): 모델 실행과 검색에 사용할 설정.
- model (ReplyModel | None): 대사 생성과 검증에 사용할 모델. fixture에서는 None.
- question_search: 첫 노드에서 공개 진술을 찾는 검색기 또는 None.

**반환값**

- None: 필요한 설정과 초기값을 저장한다.

## `InterrogationGraph.preprocess_agent`

[소스 선언](../../../../../../app/dialogue/services/reply/dialogue_interrogation_graph.py#L78)

```python
async def preprocess_agent(self, state: InterrogationState, runtime: Runtime[asyncio.Timeout]) -> dict:
    ...
```

첫 노드에서 진술 검색과 프롬프트 구성을 수행한다.

**인자**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.
- runtime: 검색 뒤 시작할 생성·검증 제한 시간을 제공하는 그래프 실행 문맥.

**반환값**

- dict: 생성 프롬프트, 검증 단위와 초기 생성 횟수.

## `InterrogationGraph.inference_agent`

[소스 선언](../../../../../../app/dialogue/services/reply/dialogue_interrogation_graph.py#L99)

```python
async def inference_agent(self, state: InterrogationState) -> dict:
    ...
```

생성 에이전트에 후보 대사 작성을 맡긴다.

**인자**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

**반환값**

- dict: 후보 대사와 시도 횟수 또는 실행 오류 상태.

## `InterrogationGraph.validation_agent`

[소스 선언](../../../../../../app/dialogue/services/reply/dialogue_interrogation_graph.py#L111)

```python
async def validation_agent(self, state: InterrogationState) -> dict:
    ...
```

검증 에이전트에 후보 대사의 사실 검사를 맡긴다.

**인자**

- state (InterrogationState): 이번 질문의 입력, 후보 대사와 시도 횟수.

**반환값**

- dict: 최종 검증 응답.

## `InterrogationGraph.generate`

[소스 선언](../../../../../../app/dialogue/services/reply/dialogue_interrogation_graph.py#L123)

```python
async def generate(self, request: CharacterReplyRequest, *, search_turn: SearchTurn | None=None) -> CharacterReplyResponse:
    ...
```

그래프를 실행한다. 검색과 생성·검증에는 각각 제한 시간을 적용한다.

**인자**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- search_turn: 게임 규칙이 승인한 자유 질문 검색 정보 또는 None.

**반환값**

- CharacterReplyResponse: 검증을 통과한 응답 또는 시간 초과 시 중립 응답.
