# tests/test_paraphrase_generation.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../tests/test_paraphrase_generation.py)

## 역할과 읽는 순서

실제 사건 승인 데이터로 재서술 허용·호출별 디코딩·사실 변조 거절을 검사한다.

모의 검증 판정은 그래프 계약을 확인하기 위한 것이며 실제 Qwen 품질 측정은 아니다.

테스트 파일은 실제 프로젝트 데이터를 사용하되 fixture와 모의 모델을 구분합니다. 테스트 통과는 GPU 품질의 독립 검증이 아닙니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## make_request

[원본 19번째 줄](../../../tests/test_paraphrase_generation.py#L19)

프로젝트의 윤재혁 소개 원문을 실제 승인 계획으로 가져온다.

### 입력과 처리

```python
def make_request(client):
```

### 실제 코드

````python
def make_request(client):
    """프로젝트의 윤재혁 소개 원문을 실제 승인 계획으로 가져온다."""
    service = client.app.state.service
    state = service.engine.initial(str(uuid4()))
    command = Interrogate(request_id=uuid4(), expected_revision=0, suspect_id='yoon', question='자기소개를 해주세요.')
    return service.dialogue_request(state, command, service.planner.prepare(state, command))
````

## test_generation_samples_but_verification_does_not

[원본 27번째 줄](../../../tests/test_paraphrase_generation.py#L27)

동일 모델이어도 생성 자유도가 검증 JSON 호출에 전달되지 않아야 한다.

### 입력과 처리

```python
def test_generation_samples_but_verification_does_not():
```

### 실제 코드

````python
def test_generation_samples_but_verification_does_not():
    """동일 모델이어도 생성 자유도가 검증 JSON 호출에 전달되지 않아야 한다."""
    settings = Settings(api_key='test-long-enough-secret', _env_file=None,
                        dialogue_temperature=0.75, dialogue_top_p=0.92, dialogue_repetition_penalty=1.08)
    assert decoding_options(settings, 'dialogue') == {
        'do_sample': True, 'temperature': 0.75, 'top_p': 0.92, 'repetition_penalty': 1.08}
    assert decoding_options(settings, 'verification') == {'do_sample': False}
    settings.dialogue_temperature = 0
    assert decoding_options(settings, 'dialogue') == {'do_sample': False}
    with pytest.raises(ValueError):
        decoding_options(settings, 'unknown')
````

## test_sampling_settings_reject_invalid_values

[원본 42번째 줄](../../../tests/test_paraphrase_generation.py#L42)

잘못된 설정을 GPU 실행 전에 거절한다.

### 입력과 처리

```python
def test_sampling_settings_reject_invalid_values(field, value):
```

### 실제 코드

````python
def test_sampling_settings_reject_invalid_values(field, value):
    """잘못된 설정을 GPU 실행 전에 거절한다."""
    with pytest.raises(ValidationError):
        Settings(api_key='test-long-enough-secret', _env_file=None, **{field: value})
````

## test_nonverbatim_reply_passes_graph_with_semantic_evidence

[원본 48번째 줄](../../../tests/test_paraphrase_generation.py#L48)

원문 부분 문자열이 없어도 별도 의미 판정과 규칙 검사를 통과하면 stop으로 반환한다.

### 입력과 처리

```python
async def test_nonverbatim_reply_passes_graph_with_semantic_evidence(client):
```

async 함수이므로 호출자는 await로 결과를 기다립니다. 대기 중 다른 요청이 실행될 수 있어 revision과 잠금 처리가 필요합니다.

주요 분기 조건은 `purpose == 'dialogue'`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
async def test_nonverbatim_reply_passes_graph_with_semantic_evidence(client):
    """원문 부분 문자열이 없어도 별도 의미 판정과 규칙 검사를 통과하면 stop으로 반환한다."""
    request = make_request(client)
    reply = '회장님의 법률 업무와 재산 관리를 곁에서 담당해 왔습니다. 오늘 찾아온 건 유언장을 변경하는 일을 처리하기 위해서입니다.'
    assert all(fact.text not in reply for fact in request.allowed_facts)

    class ParaphraseModel:
        """두 승인 문장의 의미가 두 후보 문장에 있다는 판정을 명시적으로 제공한다."""
        model_version = 'paraphrase-contract-model'

        def __init__(self):
            self.purposes = []

        async def generate(self, messages, *, purpose='dialogue'):
            """호출 목적을 기록하여 생성과 검증의 디코딩 분리 연결을 검사한다."""
            self.purposes.append(purpose)
            if purpose == 'dialogue':
                return reply
            context = json.loads(messages[1]['content'])
            assert len(context['verification_units']) == 2
            return json.dumps({'checks': [[0, True, [0]], [1, True, [1]]],
                'has_contradiction': False, 'has_unsupported_claims': False,
                'history_consistent': True, 'persona_consistent': True, 'uncertain': False})

    model = ParaphraseModel()
    response = await InterrogationGraph(client.app.state.service.settings, model).generate(request)
    assert response.finish_reason == 'stop'
    assert response.reply == reply
    assert response.used_fact_ids == ['yoon-profile']
    assert model.purposes == ['dialogue', 'verification']
````

## test_style_freedom_does_not_authorize_new_quantities

[원본 80번째 줄](../../../tests/test_paraphrase_generation.py#L80)

재서술을 허용해도 승인되지 않은 사건 금액을 추가할 권한은 없다.

### 입력과 처리

```python
def test_style_freedom_does_not_authorize_new_quantities(client):
```

### 실제 코드

````python
def test_style_freedom_does_not_authorize_new_quantities(client):
    """재서술을 허용해도 승인되지 않은 사건 금액을 추가할 권한은 없다."""
    request = make_request(client)
    assert critical_claim_error(request, '저는 회장님의 업무를 맡아왔고 3억 원을 받았습니다.') == 'unapproved_quantity_claim'
````

## test_prompts_preserve_facts_but_allow_rewording

[원본 86번째 줄](../../../tests/test_paraphrase_generation.py#L86)

생성에는 재서술 지침을, 검증에는 의미 동등 표현 허용 지침을 전달한다.

### 입력과 처리

```python
def test_prompts_preserve_facts_but_allow_rewording(client):
```

### 실제 코드

````python
def test_prompts_preserve_facts_but_allow_rewording(client):
    """생성에는 재서술 지침을, 검증에는 의미 동등 표현 허용 지침을 전달한다."""
    request = make_request(client)
    settings = client.app.state.service.settings
    messages = build_messages(request, settings)
    context = json.loads(messages[1]['content'])
    assert context['approved_facts'] == [fact.model_dump() for fact in request.allowed_facts]
    assert context['required_fact_ids'] == request.required_fact_ids
    assert '문장 자체를 복사할 필요는 없지만' in messages[0]['content']
    verification = build_verification_messages(request, settings, '대사 예시')
    assert '같은 의미이면 허용' in verification[0]['content']
````

