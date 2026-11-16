# `app/investigation/engine.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/investigation/engine.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 198줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

자료 열람·진술·쟁점·추론·단계·고발 규칙. LLM은 이 상태를 직접 수정하지 않는다.

## 함께 읽을 코드

- [app/investigation/accusation.py](accusation.md)
- [app/investigation/evidence.py](evidence.md)
- [app/investigation/testimony.py](testimony.md)

## `utc_now`

[소스 선언 위치](../../../../app/investigation/engine.py#L13)

```python
def utc_now():
    ...
```

저장 시각을 타임존이 있는 ISO 문자열로 만든다.

**파라미터**

- 없음.

**반환값**

str: UTC 시간대 정보가 포함된 현재 시각의 ISO 문자열.

## `Engine`

[소스 선언 위치](../../../../app/investigation/engine.py#L25)

```python
class Engine:
    ...
```

정적 데이터와 실제 획득 기록만으로 판정하는 Python 게임 엔진.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

**반환값**

Engine: 위 역할을 수행하도록 생성된 객체.

## `Engine.__init__`

[소스 선언 위치](../../../../app/investigation/engine.py#L35)

```python
def __init__(self, catalog):
    ...
```

내부 사건·규칙 저장소를 연결한다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `Engine.initial`

[소스 선언 위치](../../../../app/investigation/engine.py#L47)

```python
def initial(self, game_id):
    ...
```

새 수사는 새로운 ID로 시작한다. 예전 수사에 늦은 응답이 반영되지 않는다.

**파라미터**

- game_id: 조회하거나 변경할 수사의 식별자.

**반환값**

dict: 질문과 획득 자료가 초기화된 새 수사 상태.

## `Engine.require_active`

[소스 선언 위치](../../../../app/investigation/engine.py#L65)

```python
def require_active(self, state):
    ...
```

버전 변경과 종결 후 변경 요청을 거절한다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.

**반환값**

None: 반환값 없음.

## `Engine.examine`

[소스 선언 위치](../../../../app/investigation/engine.py#L79)

```python
def examine(self, state, command):
    ...
```

현재 단계의 실제 자료만 열람한다. 중복은 개수·revision을 늘리지 않는다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

**반환값**

dict: 열람 처리한 원본 자료의 식별자.

## `Engine.record_plan`

[소스 선언 위치](../../../../app/investigation/engine.py#L91)

```python
def record_plan(self, state, plan, response):
    ...
```

검증된 응답이 나온 뒤에만 질문·대화·쟁점·진술을 일괄 반영한다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- plan: 게임 규칙이 승인한 사실과 기록 예정 정보를 담은 계획.
- response: 검사하거나 저장할 최종 대사 응답.

**반환값**

dict: 기록한 대사, 종료 사유, 모델 버전과 사용 사실 ID.

## `Engine.readable_source`

[소스 선언 위치](../../../../app/investigation/engine.py#L104)

```python
def readable_source(self, state, source):
    ...
```

존재뿐 아니라 실제 획득·단계 조건도 검사한다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- source: 열람 가능 여부를 검사할 자료 종류와 식별자.

**반환값**

None: 출처 열람 조건을 확인한다. 미획득 자료면 HTTPException을 낸다.

## `Engine.infer`

[소스 선언 위치](../../../../app/investigation/engine.py#L116)

```python
def infer(self, state, command):
    ...
```

직접 선택한 정확한 조합과 단계가 일치하면 고정 결론을 만든다. LLM은 사용하지 않는다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

**반환값**

dict: 확보한 출처 조합으로 만든 추론 문서의 사본.

## `Engine.readiness`

[소스 선언 위치](../../../../app/investigation/engine.py#L128)

```python
def readiness(self, state):
    ...
```

입증 진행 개수를 계산한다. 진행도와 무관하게 미종결 수사는 고발할 수 있다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.

**반환값**

dict: 확보한 필수 추론·쟁점 수와 고발 가능 여부.

## `Engine.advance`

[소스 선언 위치](../../../../app/investigation/engine.py#L150)

```python
def advance(self, state, command):
    ...
```

단계 전환 조건을 확인한 뒤 자동 자료와 단계를 함께 변경한다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

**반환값**

dict: 변경된 조사 단계.

## `Engine.covered`

[소스 선언 위치](../../../../app/investigation/engine.py#L176)

```python
def covered(self, state, ids):
    ...
```

제출한 추론이 뒷받침하는 원본 증거를 구한다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- ids: 실제 획득하여 제출한 추론 증거 식별자 목록.

**반환값**

set[str]: 제출한 추론이 뒷받침하는 실제 열람 원본 증거 ID.

## `Engine.accuse`

[소스 선언 위치](../../../../app/investigation/engine.py#L188)

```python
def accuse(self, state, command):
    ...
```

고발 규칙 담당자에게 제출 근거와 정답 선택 평가를 맡긴다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

**반환값**

dict: 정답 일치, 점수, 제출 근거 평가와 사건 해설.
