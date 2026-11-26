# `app/dialogue/services/model/dialogue_local_model.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/dialogue/services/model/dialogue_local_model.py)

Qwen 로컬 추론 실행기. 학습하지 않고 NF4 양자화 및 기존 LoRA 어댑터를 로딩한다.

## `decoding_options`

[소스 선언](../../../../../../app/dialogue/services/model/dialogue_local_model.py#L17)

```python
def decoding_options(settings: Settings, purpose: GenerationPurpose) -> dict:
    ...
```

대사는 표현을 샘플링하고 구조화된 질문 해석과 검증은 greedy로 실행한다.

temperature는 다음 단어 선택의 자유도, top_p는 선택 후보의 누적 확률 범위다.
사실 공개 권한을 늘리는 설정이 아니며 생성 후 의미 검증은 그대로 수행한다.
검증 JSON에는 다양성이 필요 없으므로 샘플링 옵션을 전달하지 않는다.

**인자**

- settings (Settings): 모델 실행과 검색에 사용할 설정.
- purpose (GenerationPurpose): 대사 생성, 의미 검증 또는 질문 분석.

**반환값**

- dict: 대사 샘플링 또는 검증 greedy 실행 옵션.

## `ReplyModel`

[소스 선언](../../../../../../app/dialogue/services/model/dialogue_local_model.py#L43)

```python
class ReplyModel(Protocol):
    ...
```

실제 GPU 모델과 테스트용 가짜 모델이 공유하는 최소 인터페이스.

**인자**

- model_version (str): 응답에 표시할 모델과 어댑터의 버전 이름.

**반환값**

- ReplyModel: 위 역할을 수행하도록 생성된 객체.

## `ReplyModel.generate`

[소스 선언](../../../../../../app/dialogue/services/model/dialogue_local_model.py#L55)

```python
async def generate(self, messages: list[dict[str, str]], *, purpose: GenerationPurpose='dialogue') -> str:
    ...
```

호출 목적에 맞는 디코딩으로 생성한 원본 문자열을 반환한다.

**인자**

- messages (list[dict[str, str]]): 모델에 전달할 역할별 프롬프트 목록.
- purpose (GenerationPurpose): 대사 생성, 의미 검증 또는 질문 분석.

**반환값**

- str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `ModelContextError`

[소스 선언](../../../../../../app/dialogue/services/model/dialogue_local_model.py#L70)

```python
class ModelContextError(ValueError):
    ...
```

승인 사실을 보존한 프롬프트가 입력 토큰 예산을 초과했다.

**인자**

- 없음.

**반환값**

- ModelContextError: 위 역할을 수행하도록 생성된 객체.

## `LocalQwenModel`

[소스 선언](../../../../../../app/dialogue/services/model/dialogue_local_model.py#L81)

```python
class LocalQwenModel:
    ...
```

프로세스당 한 번 로딩하는 4비트 Qwen과 선택적 PEFT 어댑터.

동기 GPU 작업은 별도 스레드에서 실행한다. HTTP 요청이 취소되어도 실제 추론이
끝날 때까지 잠금을 유지하여 GPU에 다음 추론이 겹쳐 실행되지 않게 한다.

**인자**

- settings (Settings): 모델 실행과 검색에 사용할 설정.

**반환값**

- LocalQwenModel: 위 역할을 수행하도록 생성된 객체.

## `LocalQwenModel.__init__`

[소스 선언](../../../../../../app/dialogue/services/model/dialogue_local_model.py#L94)

```python
def __init__(self, settings: Settings) -> None:
    ...
```

설정과 실행 잠금을 준비한다. 가중치는 load()에서 로딩한다.

**인자**

- settings (Settings): 모델 실행과 검색에 사용할 설정.

**반환값**

- None: 필요한 설정과 초기값을 저장한다.

## `LocalQwenModel.load`

[소스 선언](../../../../../../app/dialogue/services/model/dialogue_local_model.py#L111)

```python
def load(self) -> None:
    ...
```

CUDA에서 NF4 + double quantization으로 로딩한다. 어댑터가 없으면 기본 모델이다.

**인자**

- 없음.

**반환값**

- None: 반환값 없음.

## `LocalQwenModel._generate_sync`

[소스 선언](../../../../../../app/dialogue/services/model/dialogue_local_model.py#L122)

```python
def _generate_sync(self, messages: list[dict[str, str]], purpose: GenerationPurpose='dialogue') -> str:
    ...
```

Qwen 채팅 템플릿으로 추론하고 입력 토큰을 제외한 생성 부분만 디코딩한다.

**인자**

- messages (list[dict[str, str]]): 모델에 전달할 역할별 프롬프트 목록.
- purpose (GenerationPurpose): 대사 생성, 의미 검증 또는 질문 분석.

**반환값**

- str: 입력 프롬프트를 제외하고 디코딩한 생성 원문.

## `LocalQwenModel.generate`

[소스 선언](../../../../../../app/dialogue/services/model/dialogue_local_model.py#L191)

```python
async def generate(self, messages: list[dict[str, str]], *, purpose: GenerationPurpose='dialogue') -> str:
    ...
```

GPU 추론을 직렬화한다. 취소되어도 실행 중인 스레드의 잠금은 조기에 풀지 않는다.

**인자**

- messages (list[dict[str, str]]): 모델에 전달할 역할별 프롬프트 목록.
- purpose (GenerationPurpose): 대사 생성, 의미 검증 또는 질문 분석.

**반환값**

- str: 호출 목적에 맞게 생성한 모델 출력 원문.
