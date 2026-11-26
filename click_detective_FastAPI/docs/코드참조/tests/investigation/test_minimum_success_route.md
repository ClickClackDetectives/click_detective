# `tests/investigation/test_minimum_success_route.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/investigation/test_minimum_success_route.py)

현재 채점 하한 경로와 중요 쟁점까지 확보하는 경로를 실제 데이터·API로 비교한다.

## `data`

[소스 선언](../../../../tests/investigation/test_minimum_success_route.py#L8)

```python
def data(name):
    ...
```

프런트엔드가 아닌 백엔드 자체 사건 데이터를 읽는다.

**인자**

- name: 읽을 파일 또는 실행할 사례의 이름.

**반환값**

- 프런트엔드가 아닌 백엔드 자체 사건 데이터를 읽는다.

## `infer`

[소스 선언](../../../../tests/investigation/test_minimum_success_route.py#L20)

```python
def infer(play, key):
    ...
```

현재 규칙에서 지정한 정확한 출처 조합으로 추론을 생성한다.

**인자**

- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.
- key: 사건 데이터 항목의 식별자.

**반환값**

- dict: 확보한 출처 조합으로 만든 추론 문서의 사본.

## `prepare_shared_case`

[소스 선언](../../../../tests/investigation/test_minimum_success_route.py#L36)

```python
def prepare_shared_case(play):
    ...
```

두 경로에 공통인 4회 심문·14개 원본·핵심 선행 추론을 API로 마련한다.

**인자**

- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `submit_core_accusation`

[소스 선언](../../../../tests/investigation/test_minimum_success_route.py#L80)

```python
def submit_core_accusation(play):
    ...
```

이미 생성한 다섯 핵심 추론을 제출해 채점과 종결을 확인한다.

**인자**

- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

**반환값**

- 이미 생성한 다섯 핵심 추론을 제출해 채점과 종결을 확인한다.

## `test_five_question_success_route`

[소스 선언](../../../../tests/investigation/test_minimum_success_route.py#L100)

```python
def test_five_question_success_route(play):
    ...
```

5회 경로는 채점상 통과하지만 중요 쟁점 전체의 발견을 보장하지 않음을 비교한다.

**인자**

- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_minimum_important_findings_route`

[소스 선언](../../../../tests/investigation/test_minimum_success_route.py#L127)

```python
def test_minimum_important_findings_route(play):
    ...
```

중요 쟁점 5개를 포함한 8회 심문·6개 쟁점·7개 추론의 입증 경로를 확인한다.

**인자**

- play: 현재 수사 상태를 갱신하며 행동 API를 호출하는 테스트 도우미.

**반환값**

- None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
