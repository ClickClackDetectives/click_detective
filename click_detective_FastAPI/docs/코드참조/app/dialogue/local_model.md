# `app/dialogue/local_model.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/dialogue/local_model.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 221줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

Qwen 로컬 추론 실행기. 학습하지 않고 NF4 양자화 및 기존 LoRA 어댑터를 로딩한다.

## 함께 읽을 코드

- [app/config.py](../config.md)
- [app/dialogue/diagnostics.py](diagnostics.md)
- [app/dialogue/model_loading.py](model_loading.md)

## `decoding_options`

[소스 선언 위치](../../../../app/dialogue/local_model.py#L15)

```python
def decoding_options(settings: Settings, purpose: GenerationPurpose) -> dict:
    ...
```

대사는 표현을 샘플링하고 검증은 greedy로 실행한다.

temperature는 다음 단어 선택의 자유도, top_p는 선택 후보의 누적 확률 범위다.
사실 공개 권한을 늘리는 설정이 아니며 생성 후 의미 검증은 그대로 수행한다.
검증 JSON에는 다양성이 필요 없으므로 샘플링 옵션을 전달하지 않는다.

**파라미터**

- settings (Settings): 모델 실행과 검색에 사용할 설정.
- purpose (GenerationPurpose): 모델 호출 목적. dialogue는 생성, verification은 검증이다.

**반환값**

dict: 대사 샘플링 또는 검증 greedy 실행 옵션.

## `ReplyModel`

[소스 선언 위치](../../../../app/dialogue/local_model.py#L41)

```python
class ReplyModel(Protocol):
    ...
```

실제 GPU 모델과 테스트용 가짜 모델이 공유하는 최소 인터페이스.

**파라미터**

- model_version (str): 응답에 표시할 모델과 어댑터의 버전 이름.

**반환값**

ReplyModel: 위 역할을 수행하도록 생성된 객체.

## `ReplyModel.generate`

[소스 선언 위치](../../../../app/dialogue/local_model.py#L53)

```python
async def generate(
    self, messages: list[dict[str, str]], *, purpose: GenerationPurpose = "dialogue"
) -> str:
    ...
```

호출 목적에 맞는 디코딩으로 생성한 원본 문자열을 반환한다.

**파라미터**

- messages (list[dict[str, str]]): 모델에 전달할 역할별 프롬프트 목록.
- purpose (GenerationPurpose): 모델 호출 목적. dialogue는 생성, verification은 검증이다.

**반환값**

str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `ModelContextError`

[소스 선언 위치](../../../../app/dialogue/local_model.py#L68)

```python
class ModelContextError(ValueError):
    ...
```

승인 사실을 보존한 프롬프트가 입력 토큰 예산을 초과했다.

**파라미터**

- 없음.

**반환값**

ModelContextError: 위 역할을 수행하도록 생성된 객체.

## `LocalQwenModel`

[소스 선언 위치](../../../../app/dialogue/local_model.py#L79)

```python
class LocalQwenModel:
    ...
```

프로세스당 한 번 로딩하는 4비트 Qwen과 선택적 PEFT 어댑터.

동기 GPU 작업은 별도 스레드에서 실행한다. HTTP 요청이 취소되어도 실제 추론이
끝날 때까지 잠금을 유지하여 GPU에 다음 추론이 겹쳐 실행되지 않게 한다.

**파라미터**

- settings (Settings): 모델 실행과 검색에 사용할 설정.

**반환값**

LocalQwenModel: 위 역할을 수행하도록 생성된 객체.

## `LocalQwenModel.__init__`

[소스 선언 위치](../../../../app/dialogue/local_model.py#L92)

```python
def __init__(self, settings: Settings) -> None:
    ...
```

설정과 실행 잠금을 준비한다. 가중치는 load()에서 로딩한다.

**파라미터**

- settings (Settings): 모델 실행과 검색에 사용할 설정.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `LocalQwenModel.load`

[소스 선언 위치](../../../../app/dialogue/local_model.py#L109)

```python
def load(self) -> None:
    ...
```

CUDA에서 NF4 + double quantization으로 로딩한다. 어댑터가 없으면 기본 모델이다.

**파라미터**

- 없음.

**반환값**

None: 반환값 없음.

## `LocalQwenModel._generate_sync`

[소스 선언 위치](../../../../app/dialogue/local_model.py#L120)

```python
def _generate_sync(
    self, messages: list[dict[str, str]], purpose: GenerationPurpose = "dialogue"
) -> str:
    ...
```

Qwen 채팅 템플릿으로 추론하고 입력 토큰을 제외한 생성 부분만 디코딩한다.

**파라미터**

- messages (list[dict[str, str]]): 모델에 전달할 역할별 프롬프트 목록.
- purpose (GenerationPurpose): 모델 호출 목적. dialogue는 생성, verification은 검증이다.

**반환값**

str: 입력 프롬프트를 제외하고 디코딩한 생성 원문.

## `LocalQwenModel.generate`

[소스 선언 위치](../../../../app/dialogue/local_model.py#L188)

```python
async def generate(
    self, messages: list[dict[str, str]], *, purpose: GenerationPurpose = "dialogue"
) -> str:
    ...
```

GPU 추론을 직렬화한다. 취소되어도 실행 중인 스레드의 잠금은 조기에 풀지 않는다.

**파라미터**

- messages (list[dict[str, str]]): 모델에 전달할 역할별 프롬프트 목록.
- purpose (GenerationPurpose): 모델 호출 목적. dialogue는 생성, verification은 검증이다.

**반환값**

str: 호출 목적에 맞게 생성한 모델 출력 원문.

## `LocalQwenModel.generate.release_after_completion`

[소스 선언 위치](../../../../app/dialogue/local_model.py#L207)

```python
def release_after_completion(completed: asyncio.Task) -> None:
    ...
```

실제 GPU 작업이 끝나면 잠금을 풀고 취소 후의 예외도 회수한다.

**파라미터**

- completed (asyncio.Task): 실제 모델 추론이 끝난 비동기 작업.

**반환값**

None: 반환값 없음.
