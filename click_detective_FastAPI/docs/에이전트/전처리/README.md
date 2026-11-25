# 전처리 에이전트

[에이전트 목차](../README.md) · 다음: [생성 에이전트](../생성/README.md)

전처리는 AI가 답변을 쓰기 전에 사용할 자료를 준비하는 일이다. 이 프로젝트에서는 **공개할 사실 선택**과 **이미 승인한 사실로 프롬프트 만들기**를 구분한다.

## 1. 그래프 실행 전에 공개 조건 확인

```python
def prepare(self, state, command, *, search_free=False):
    ...
```

담당: `Planner.prepare` — [실제 코드](../../../app/dialogue/preprocess_agent/planning.py)

- `state`: 질문 수, 획득 자료, 과거 대화 등 현재 수사 상태
- `command`: 이번 질문과 대상 인물, 제시한 자료
- 반환값: `ReplyPlan`. 이번에 말할 사실과 나중에 기록할 진술·쟁점 계획

처리 순서는 다음과 같다.

1. 존재하는 인물인지, 질문 한도가 남았는지 확인한다.
2. 명시한 주제가 있으면 해당 인물의 심문 주제인지 확인한다.
3. 같은 인물에게 과거에 제시한 자료와 이번 자료를 중복 없이 모은다.
4. 실제 획득한 자료인지 검사하고 원본 출처를 확인한다.
5. 자료 조건으로 새로 공개할 쟁점이 있으면 인정 진술을 선택한다.
6. 명시한 주제에 해당하는 진술을 고른다. E5가 켜진 자유 질문은 이 단계의 선택을 벡터 검색에 맡긴다.
7. 원래 수사 상태를 확정 변경하지 않고 계획을 반환한다.

자료 확인은 [approval_materials.py](../../../app/dialogue/preprocess_agent/approval_materials.py)에서 담당한다. 명시 주제와 새 인정 진술은 서버가 정한 원문을 곧바로 사용한다. 벡터 검색을 쓰지 않는 모드의 자유 질문은 [free_questions.py](../../../app/dialogue/preprocess_agent/free_questions.py)의 규칙으로 처리한다.

`GameService.dialogue_request`는 이 계획을 대화 요청으로 바꾼다. 검색할 자유 질문은 승인 계획과 이미 공개된 쟁점 ID를 첫 노드에 함께 전달한다.

## 2. 그래프의 전처리 단계 실행

```python
async def preprocess_agent(self, state: InterrogationState) -> dict:
    ...
```

담당: `PreprocessAgent.preprocess_agent` — [실제 코드](../../../app/dialogue/preprocess_agent/agent.py) · [코드 참조](../../코드참조/app/dialogue/preprocess_agent/agent.md)

- `state`: 대화 요청과 자유 질문의 검색 문맥을 포함하는 작업 기록
- 반환값: 검색 결과를 반영한 `request`, 생성용 `messages`와 초기 `attempt=0`

1. 자유 질문에 [question_search.py](../../../app/dialogue/preprocess_agent/question_search.py)를 호출한다. 현재 인물이 공개할 수 있는 후보에서 E5와 ChromaDB로 검색하고 Kiwi BM25로 재정렬한다.
2. 선택한 진술을 승인 사실과 필수 사실 ID에 반영하고, 같은 진술을 게임 기록용 계획에 넣는다. 명시 주제와 새 인정 진술은 검색을 건너뛴다.
3. 승인 사실을 문장 단위로 나눈다. 검증 문장이 256개를 넘으면 HTTP 422로 거절한다.
4. `build_messages`로 프롬프트를 만든다. 기본 v1의 검색 결과가 비면 검증 단계가 곧바로 고정 중립 답변을 확정한다. 진술이 선택되면 생성 단계로 전달하며, 재생성에서도 같은 검색 결과를 사용한다.

전처리에서 E5 임베딩 모델을 실행한다. 대사 작성용 Qwen은 생성 단계에서 호출한다.

## 3. 생성 프롬프트 만들기

[프롬프트 코드](../../../app/dialogue/preprocess_agent/prompt.py)는 승인 사실을 입력받은 순서대로 전달한다. [대화 요청 형식](../../../app/dialogue/schemas.py)은 사실 ID가 중복되거나 필수 ID가 승인 범위를 벗어나면 요청을 거절한다. 질문·이력·자료는 참고 데이터이며, 공개 범위는 승인 사실에서 정한다.
