# `app/investigation/presentation.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/investigation/presentation.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 204줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

서버가 화면용 목록·진행률·타임라인·가능한 행동을 계산한다. 비공개 규칙은 제외한다.

## 함께 읽을 코드

- [app/investigation/material_display.py](material_display.md)
- [app/investigation/result_display.py](result_display.md)
- [app/investigation/timeline.py](timeline.md)

## `Presenter`

[소스 선언 위치](../../../../app/investigation/presentation.py#L11)

```python
class Presenter:
    ...
```

Next.js는 반환된 값을 표시한다. 진행·공개 조건을 다시 계산할 필요가 없다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- engine: 게임 진행과 행동의 조건을 판정하는 객체.

**반환값**

Presenter: 위 역할을 수행하도록 생성된 객체.

## `Presenter.__init__`

[소스 선언 위치](../../../../app/investigation/presentation.py#L22)

```python
def __init__(self, catalog, engine):
    ...
```

같은 규칙 서비스로 UI 준비 상태와 실제 판정을 일치시킨다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- engine: 게임 진행과 행동의 조건을 판정하는 객체.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `Presenter.materials`

[소스 선언 위치](../../../../app/investigation/presentation.py#L35)

```python
def materials(self, state):
    ...
```

공개 가능한 제목·요약을 반환하고 본문·원본 파일 경로는 상세 API로 분리한다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.

**반환값**

list[dict]: 현재 공개 가능한 원본·진술·추론의 제목과 요약 목록.

## `Presenter.describe_source`

[소스 선언 위치](../../../../app/investigation/presentation.py#L46)

```python
def describe_source(self, state, ref):
    ...
```

실제 획득 출처를 화면용 번호·제목·분류로 바꾼다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- ref: 자료 종류와 식별자를 담은 출처 참조.

**반환값**

dict: 출처의 번호·제목·분류와 설명.

## `Presenter.timeline`

[소스 선언 위치](../../../../app/investigation/presentation.py#L58)

```python
def timeline(self, state):
    ...
```

실제 확보한 진술·문서만 공개 시간표에 추가한다. 숨겨진 실제 행적은 사용하지 않는다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.

**반환값**

list[dict]: 공개된 자료로 구성하여 시작 시각·ID 순으로 정렬한 시간표.

## `Presenter.state`

[소스 선언 위치](../../../../app/investigation/presentation.py#L69)

```python
def state(self, state):
    ...
```

명시적 공개 DTO를 구성한다. 모든 규칙·미발견 정답 후보를 반환하지 않는다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.

**반환값**

dict: 내부 비공개 규칙을 제외한 화면용 수사 상태.
