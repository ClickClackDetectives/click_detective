# 멀티 에이전트 전체 흐름

[전체 목차](../README.md) · [전처리](전처리/README.md) · [생성](생성/README.md) · [검증](검증/README.md)

수사 서비스가 승인 문맥을 준비하면 대화 그래프가 전처리, 생성, 검증을 순서대로 실행한다. 그래프의 중간 상태는 요청 단위로 관리한다.

| 단계 | 담당 클래스 | 역할 | 대화 LLM 호출 |
|---|---|---|---|
| 1. 전처리 | `PreprocessAgent` | 승인 사실 검색·생성 자료 준비 | 없음 |
| 2. 생성 | `InferenceAgent` | 자연스러운 후보 대사 작성 | `purpose="dialogue"` |
| 3. 검증 | `ValidationAgent` | 규칙·모델 판정과 일부·중립 응답 결정 | 의미 검사에서 `purpose="verification"` |

## 세 단계를 연결하는 클래스

```python
class InterrogationGraph:
    ...
```

[실제 코드](../../app/dialogue/services/reply/dialogue_interrogation_graph.py) · [클래스·함수 참조](../코드참조/app/dialogue/services/reply/dialogue_interrogation_graph.md)

생성할 때 설정과 공용 모델을 받아 세 에이전트 객체를 만든다. LangGraph에 `preprocess_agent`, `inference_agent`, `validation_agent` 노드를 연결한다. 그래프의 각 메서드는 해당 에이전트 객체에 작업을 전달한다.

```mermaid
flowchart TD
    A[수사 서비스의 승인 계획] --> B[전처리와 검색]
    B --> C[후보 대사 생성]
    C --> D[규칙과 필요 시 모델 검증]
    D --> E[검증된 전체·일부 또는 중립 응답]
    E --> F[수사 기록 확정]
```

서버 규칙이 먼저 공개 사실을 결정한다. 에이전트가 정답이나 새 쟁점을 임의로 결정하지 않는다. 그래프는 순차 실행하며, GPU 모델 호출도 잠금으로 직렬화한다.

## 함께 사용하는 작업 기록

```python
class InterrogationState(TypedDict, total=False):
    ...
```

[실제 코드](../../app/dialogue/dto/dialogue_graph_state.py)

| 값 | 의미 |
|---|---|
| `request` | 질문·인물·승인 사실·필수 사실 ID |
| `messages` | 승인 사실과 질문을 담은 생성 프롬프트 |
| `raw_output` | 생성한 후보 대사 원문 |
| `error_status` | 모델 실행 오류 |
| `response` | 최종 응답 |

각 노드는 필요한 결과만 딕셔너리로 반환하고, LangGraph가 작업 기록을 다음 단계로 전달한다. 중간 작업 기록 전체를 게임 DB에 저장하지 않는다.

## 제한 시간과 결과

`InterrogationGraph.generate`는 생성·검증에 시간 제한을 적용한다. 자유 질문 검색에는 별도의 실행 제한을 적용한다.

`finish_reason`에는 `stop`, `fixed`, `fallback`과 `partial`, `neutral`이 있다. [응답과 복구](응답과_복구_정책.md)

다음으로 [전처리](전처리/README.md), [생성](생성/README.md), [검증](검증/README.md)을 순서대로 읽는다. 모델 준비는 [공용 모델](공용_모델.md), 실패 분기는 [응답·복구 정책](응답과_복구_정책.md), 검색과 표현 설정은 [검색과 표현 자유도](검색과_표현_자유도.md)를 참고한다.
