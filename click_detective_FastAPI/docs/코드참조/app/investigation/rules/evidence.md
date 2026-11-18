# `app/investigation/rules/evidence.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/investigation/rules/evidence.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 110줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

수사에서 획득한 증거의 열람과 출처 기반 추론을 처리한다.

## `examine`

[소스 선언 위치](../../../../../app/investigation/rules/evidence.py#L8)

```python
def examine(catalog, state, command):
    ...
```

현재 단계의 실제 자료만 열람한다. 중복은 개수·revision을 늘리지 않는다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

**반환값**

dict: 열람 처리한 원본 자료의 식별자.

## `readable_source`

[소스 선언 위치](../../../../../app/investigation/rules/evidence.py#L27)

```python
def readable_source(catalog, state, source):
    ...
```

존재뿐 아니라 실제 획득·단계 조건도 검사한다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- source: 열람 가능 여부를 검사할 자료 종류와 식별자.

**반환값**

None: 출처 열람 조건을 확인한다. 미획득 자료면 HTTPException을 낸다.

## `infer`

[소스 선언 위치](../../../../../app/investigation/rules/evidence.py#L50)

```python
def infer(catalog, state, command):
    ...
```

직접 선택한 정확한 조합과 단계가 일치하면 고정 결론을 만든다. LLM은 사용하지 않는다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

**반환값**

dict: 확보한 출처 조합으로 만든 추론 문서의 사본.
