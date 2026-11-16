# 전처리 에이전트

[에이전트 목차](../README.md) · 다음: [생성 에이전트](../생성/README.md)

전처리는 AI가 답변을 쓰기 전에 사용할 자료를 준비하는 일이다. 이 프로젝트에서는 **공개할 사실 선택**과 **이미 승인한 사실로 프롬프트 만들기**를 구분한다.

## 1. 그래프 실행 전에 말해도 되는 사실 선택

```python
def prepare(self, state, command):
    ...
```

담당: `Planner.prepare` — [실제 코드](../../../app/dialogue/preprocess_agent/planning.py)

- `state`: 질문 수, 획득 자료, 과거 대화 등 현재 수사 상태
- `command`: 이번 질문과 대상 인물, 제시한 자료
- 반환값: `ReplyPlan`. 이번에 말할 사실과 나중에 기록할 진술·쟁점 계획

처리 순서는 다음과 같다.

1. 존재하는 인물인지, 질문 한도가 남았는지 확인한다.
2. 명시한 주제를 검사하거나 질문에서 알려진 주제를 찾는다.
3. 같은 인물에게 과거에 제시한 자료와 이번 자료를 중복 없이 모은다.
4. 실제 획득한 자료인지 검사하고 원본 출처를 확인한다.
5. 자료 조건으로 새로 공개할 쟁점이 있으면 인정 진술을 선택한다.
6. 그 외에는 동선·관계·자유 질문에 맞는 공개 진술을 고른다.
7. 원래 수사 상태를 확정 변경하지 않고 계획을 반환한다.

자료 확인은 [approval_materials.py](../../../app/dialogue/preprocess_agent/approval_materials.py), 자유 질문 선택은 [free_questions.py](../../../app/dialogue/preprocess_agent/free_questions.py)에서 읽을 수 있다.

`GameService.dialogue_request`는 이 계획을 대화 요청으로 바꾼다. 현재 서비스는 계획의 사실 전체를 승인 사실이자 필수 사실로 지정한다.

## 2. 그래프의 전처리 단계 실행

```python
async def preprocess_agent(self, state: InterrogationState) -> dict:
    ...
```

담당: `PreprocessAgent.preprocess_agent` — [실제 코드](../../../app/dialogue/preprocess_agent/agent.py) · [코드 참조](../../코드참조/app/dialogue/preprocess_agent/agent.md)

- `state`: 승인 사실을 담은 요청을 포함하는 작업 기록
- 반환값: `messages`, `retrieval`, 초기 `attempt=0`을 담은 딕셔너리

1. 승인 사실을 문장 단위로 나눈다. 검증 문장이 256개를 넘으면 HTTP 422로 거절한다.
2. `retrieve_approved_facts`로 승인 사실 안에서 관련 내용을 찾는다.
3. 필수 사실은 점수·선택 개수와 무관하게 보존한다.
4. `build_messages`로 인물 설정, 질문, 승인 사실, 필수 문장, 최근 대화를 묶는다.
5. 다음 생성 단계가 사용할 작업 기록을 반환한다.

전처리 에이전트는 모델을 직접 호출하지 않는다. 생성과 검증에서 사용하는 공용 모델 객체를 전처리에 전달할 필요도 없다.

## 3. 검색은 어디까지 가능한가?

```python
def retrieve_approved_facts(
    request: CharacterReplyRequest,
    top_k: int = 3,
    enabled: bool = True,
) -> RetrievalContext:
    ...
```

[실제 코드](../../../app/dialogue/preprocess_agent/retriever.py)

검색 대상은 `request.allowed_facts`다. 단어·두 글자 조각·명시적 사실 ID 일치로 점수를 계산한다. 벡터 DB나 새로운 검색 모델을 사용하지 않는다.

필수 사실을 먼저 포함하고 관련성이 있는 선택적 사실만 `top_k`개까지 추가한다. 점수가 같으면 먼저 승인된 사실을 선택하며, 최종 결과는 원래 승인 순서로 돌려준다. 검색이 꺼져 있으면 승인 사실 전체를 반환한다.

현재 게임 서비스는 승인 사실 전부를 필수로 지정한다. 따라서 `top_k=3`이라고 승인 사실을 세 개만 남기는 것은 아니다.

## 4. 생성 프롬프트 만들기

`build_messages`는 검색 결과가 같은 수사·사건 버전·인물에 속하는지 확인한다. 승인되지 않거나 바뀐 사실, 중복 ID, 누락된 필수 사실을 거절한다.

[프롬프트 코드](../../../app/dialogue/preprocess_agent/prompt.py)는 목록을 먼저 만든 뒤 하나의 자료 묶음으로 정리한다. 질문·이력·자료는 참고 데이터이며, 새 비밀을 공개할 권한은 승인 사실에서만 나온다.
