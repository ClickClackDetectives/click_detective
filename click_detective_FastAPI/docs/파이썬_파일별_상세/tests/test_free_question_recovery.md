# tests/test_free_question_recovery.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../tests/test_free_question_recovery.py)

## 역할과 읽는 순서

증거 없는 자유 질문과 생성 재시도 계약을 실제 사건 데이터·3노드 그래프로 회귀 검사한다.

테스트 파일은 실제 프로젝트 데이터를 사용하되 fixture와 모의 모델을 구분합니다. 테스트 통과는 GPU 품질의 독립 검증이 아닙니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## RetryingModel

[원본 14번째 줄](../../../tests/test_free_question_recovery.py#L14)

첫 생성은 필수 뒷문장을 누락하고 다음 생성은 모두 포함하는 모의 모델.

## RetryingModel.__init__

[원본 19번째 줄](../../../tests/test_free_question_recovery.py#L19)

상위 호출의 처리를 보조하는 내부 함수입니다. 아래 실제 입력·조건·반환을 확인하세요.

### 입력과 처리

```python
def __init__(self):
```

### 실제 코드

````python
def __init__(self):
        self.generation_calls = []
````

## RetryingModel.generate

[원본 22번째 줄](../../../tests/test_free_question_recovery.py#L22)

실제 GPU 없이 생성 누락→검증 거절→올바른 평문 재생성을 재현한다.

### 입력과 처리

```python
async def generate(self, messages, *, purpose="dialogue"):
```

async 함수이므로 호출자는 await로 결과를 기다립니다. 대기 중 다른 요청이 실행될 수 있어 revision과 잠금 처리가 필요합니다.

주요 분기 조건은 `'candidate_sentences' not in context`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
async def generate(self, messages, *, purpose="dialogue"):
        """실제 GPU 없이 생성 누락→검증 거절→올바른 평문 재생성을 재현한다."""
        context = json.loads(messages[1]['content'])
        if 'candidate_sentences' not in context:
            self.generation_calls.append(messages)
            required = context['required_sentences']
            return required[0] if len(self.generation_calls) == 1 else ' '.join(required)
        source = {unit['index']: unit['text'] for fact in context['approved_facts'] for unit in fact['units']}
        checks = []
        for unit in context['verification_units']:
            parts = [part['id'] for part in context['candidate_sentences'] if source[unit['index']] in part['text']]
            checks.append([unit['index'], bool(parts), parts])
        return json.dumps({'checks': checks, 'has_contradiction': False,
            'has_unsupported_claims': False, 'history_consistent': True,
            'persona_consistent': True, 'uncertain': False})
````

## test_no_evidence_question_can_retry_as_plain_text

[원본 39번째 줄](../../../tests/test_free_question_recovery.py#L39)

강민호 면담 질문의 첫 필수 문장 누락을 평문 형식을 유지하며 복구한다.

### 입력과 처리

```python
async def test_no_evidence_question_can_retry_as_plain_text(client):
```

async 함수이므로 호출자는 await로 결과를 기다립니다. 대기 중 다른 요청이 실행될 수 있어 revision과 잠금 처리가 필요합니다.

### 실제 코드

````python
async def test_no_evidence_question_can_retry_as_plain_text(client):
    """강민호 면담 질문의 첫 필수 문장 누락을 평문 형식을 유지하며 복구한다."""
    service = client.app.state.service
    state = service.engine.initial(str(uuid4()))
    command = Interrogate(request_id=uuid4(), expected_revision=0, suspect_id='kang',
                          question='와인잔에 무엇을 했는지 말해주세요')
    plan = service.planner.prepare(state, command)
    request = service.dialogue_request(state, command, plan)
    model = RetryingModel()
    response = await InterrogationGraph(service.settings, model).generate(request)
    assert response.finish_reason == 'stop'
    assert response.used_fact_ids == ['kang-meeting']
    assert all(fact.text in response.reply for fact in request.allowed_facts)
    assert len(model.generation_calls) == 2
    retry_instruction = model.generation_calls[1][-1]['content']
    assert '대사 원문만' in retry_instruction
    assert 'JSON 형식도 지키세요' not in retry_instruction
````

## test_unknown_free_question_returns_neutral_without_model

[원본 58번째 줄](../../../tests/test_free_question_recovery.py#L58)

승인 정보가 없는 질문은 502·허구 생성 대신 기존 중립 정책으로 응답한다.

### 입력과 처리

```python
def test_unknown_free_question_returns_neutral_without_model(api, client, game, monkeypatch):
```

### 실제 코드

````python
def test_unknown_free_question_returns_neutral_without_model(api, client, game, monkeypatch):
    """승인 정보가 없는 질문은 502·허구 생성 대신 기존 중립 정책으로 응답한다."""
    class NeverModel:
        """호출되면 실패하는 모델로 빈 승인 경로의 GPU 미호출을 확인한다."""
        model_version = 'never-called'

        async def generate(self, messages, *, purpose="dialogue"):
            raise AssertionError('승인 사실이 없는 질문에 모델을 호출했습니다.')

    service = client.app.state.service
    monkeypatch.setattr(service.settings, 'generation_mode', 'local')
    monkeypatch.setattr(service, 'graph', InterrogationGraph(service.settings, NeverModel()))
    response = api('POST', '/v1/games/' + game['game_id'] + '/interrogations', {
        'request_id': str(uuid4()), 'expected_revision': 0, 'suspect_id': 'kang',
        'question': '수학 문제를 풀어주세요'}, game['game_token'])
    assert response.status_code == 200
    assert response.json()['result']['finish_reason'] == 'fixed'
    assert response.json()['result']['used_fact_ids'] == []
    assert response.json()['state']['findingDetails'] == []
````

## test_false_verification_with_evidence_still_rejected

[원본 79번째 줄](../../../tests/test_free_question_recovery.py#L79)

검증 형식 안정화 과정에서도 false+근거 번호를 성공으로 수선하지 않는다.

### 입력과 처리

```python
def test_false_verification_with_evidence_still_rejected(client):
```

### 실제 코드

````python
def test_false_verification_with_evidence_still_rejected(client):
    """검증 형식 안정화 과정에서도 false+근거 번호를 성공으로 수선하지 않는다."""
    service = client.app.state.service
    state = service.engine.initial(str(uuid4()))
    command = Interrogate(request_id=uuid4(), expected_revision=0, suspect_id='kang', question='자기소개를 해주세요')
    request = service.dialogue_request(state, command, service.planner.prepare(state, command))
    report = SemanticReport(checks=[(index, False, [0]) for index, _ in enumerate(build_verification_units(request))], has_contradiction=False,
                            has_unsupported_claims=False, history_consistent=True,
                            persona_consistent=True, uncertain=False)
    with pytest.raises(OutputRejected, match='verification_evidence_mismatch'):
        InterrogationGraph._check_report_evidence(report, request, request.allowed_facts[0].text)
````

