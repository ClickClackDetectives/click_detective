# `app/investigation/services/investigation_dialogue_request.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/services/investigation_dialogue_request.py)

승인된 사실과 저장 상태를 모델에 전달할 입력으로 변환한다.

## `prepare_interrogation`

[소스 선언](../../../../../app/investigation/services/investigation_dialogue_request.py#L6)

```python
def prepare_interrogation(service, state, command):
    ...
```

수사 상태와 심문 입력을 검사하고 차감 전 모델 요청을 준비한다.

**인자**

- service: 진행 규칙, 승인 계획과 모델 요청 구성을 담당하는 서비스.
- state: 질문을 차감하기 전 수사 상태.
- command: 서버에 전송한 심문 명령.

**반환값**

- tuple: 승인 계획, 모델 요청과 자유 질문 검색 여부.

## `dialogue_request`

[소스 선언](../../../../../app/investigation/services/investigation_dialogue_request.py#L38)

```python
def dialogue_request(catalog, history_limit, state, command, plan):
    ...
```

수사 상태와 승인 계획으로 대화 요청을 만든다.

**인자**

- catalog: 사건 데이터와 인물 말투를 제공하는 객체.
- history_limit: 전송할 최근 메시지 수. 0이면 대화 이력을 생략한다.
- state: 현재 수사의 내부 상태.
- command: 사용자의 심문 명령.
- plan: 규칙이 승인한 사실과 진술 계획.

**반환값**

- CharacterReplyRequest: 승인 사실, 최근 대화와 쟁점별 내부 검증 기준을 담은 입력.
