# `app/investigation/rules/accusation.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/investigation/rules/accusation.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 154줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

고발의 근거 충족 여부와 점수를 계산한다.

## `AccusationRules`

[소스 선언 위치](../../../../../app/investigation/rules/accusation.py#L8)

```python
class AccusationRules:
    ...
```

제출한 추론 근거와 고발 선택을 평가한다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

**반환값**

AccusationRules: 위 역할을 수행하도록 생성된 객체.

## `AccusationRules.__init__`

[소스 선언 위치](../../../../../app/investigation/rules/accusation.py#L18)

```python
def __init__(self, catalog):
    ...
```

사용할 의존성과 초기 상태를 준비한다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

**반환값**

None: 필요한 설정과 초기값을 저장한다.

## `AccusationRules.covered`

[소스 선언 위치](../../../../../app/investigation/rules/accusation.py#L29)

```python
def covered(self, state, ids):
    ...
```

제출한 실제 추론의 원본 근거 중 실제 열람한 자료만 계산한다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- ids: 실제 획득하여 제출한 추론 증거 식별자 목록.

**반환값**

set[str]: 제출한 추론이 뒷받침하는 실제 열람 원본 증거 ID.

## `AccusationRules.accuse`

[소스 선언 위치](../../../../../app/investigation/rules/accusation.py#L46)

```python
def accuse(self, state, command):
    ...
```

언제든 고발을 받아 채점한다. 부족한 입증은 제출 차단 대신 점수에 반영한다.

조사 단계·발견 쟁점 수·추론 개수는 제출 조건이 아니다. 제출한 ID가 있다면
실제 확보한 서로 다른 추론인지 검사하고, 핵심 근거 충족 여부로 채점한다.

**파라미터**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

**반환값**

dict: 정답 일치, 점수, 제출 근거 평가와 사건 해설.
