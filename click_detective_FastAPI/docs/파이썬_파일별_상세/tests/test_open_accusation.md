# tests/test_open_accusation.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../tests/test_open_accusation.py)

## 역할과 읽는 순서

실제 사건 데이터로 초기·소수 근거 고발과 부족한 입증의 채점을 검사한다.

테스트 파일은 실제 프로젝트 데이터를 사용하되 fixture와 모의 모델을 구분합니다. 테스트 통과는 GPU 품질의 독립 검증이 아닙니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## selections

[원본 9번째 줄](../../../tests/test_open_accusation.py#L9)

테스트만 서버 비공개 정답을 읽어 선택 채점과 근거 채점을 분리한다.

### 입력과 처리

```python
def selections():
```

### 실제 코드

````python
def selections():
    """테스트만 서버 비공개 정답을 읽어 선택 채점과 근거 채점을 분리한다."""
    solution = json.loads((PROJECT_ROOT/'data/case/solution.private.json').read_text())['solution']
    return {'suspect_id': solution['suspectId'], 'motive': solution['motive'], 'method': solution['method']}
````

## test_initial_game_can_accuse_without_evidence

[원본 16번째 줄](../../../tests/test_open_accusation.py#L16)

1차 조사·쟁점 0·추론 0이어도 제출하고, 입증 부족은 채점으로 처리한다.

### 입력과 처리

```python
def test_initial_game_can_accuse_without_evidence(api, game, include_empty_evidence):
```

주요 분기 조건은 `include_empty_evidence`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def test_initial_game_can_accuse_without_evidence(api, game, include_empty_evidence):
    """1차 조사·쟁점 0·추론 0이어도 제출하고, 입증 부족은 채점으로 처리한다."""
    state = game['state']
    assert state['phase'] == 1
    assert state['availableActions']['accuse'] is True
    assert state['accusationReadiness']['eligible'] is True
    body = {'request_id': str(uuid4()), 'expected_revision': 0, **selections()}
    if include_empty_evidence:
        body['evidence_ids'] = []
    path = '/v1/games/' + game['game_id']
    response = api('POST', path+'/accusations', body, game['game_token'])
    assert response.status_code == 200
    verdict = response.json()['result']
    assert verdict['score'] == 75
    assert verdict['correct'] is False
    assert verdict['submittedEvidenceIds'] == []
    assert verdict['checks'][-1]['correct'] is False
    assert verdict['evidenceAssessment']['missing']
    assert response.json()['state']['availableActions']['accuse'] is False
    assert api('POST', path+'/accusations', body, game['game_token']).json() == response.json()
    repeated = api('POST', path+'/accusations', body | {'request_id':str(uuid4()), 'expected_revision':1}, game['game_token'])
    assert repeated.status_code == 409
    restored = api('GET', path, game_token=game['game_token']).json()['state']
    assert restored['verdict'] == response.json()['state']['verdict']
````

## test_single_earned_inference_can_be_submitted

[원본 42번째 줄](../../../tests/test_open_accusation.py#L42)

실제 1차 추론 하나만 확보해 제출해도 최소 5개 제한에 막히지 않는다.

### 입력과 처리

```python
def test_single_earned_inference_can_be_submitted(play):
```

### 실제 코드

````python
def test_single_earned_inference_can_be_submitted(play):
    """실제 1차 추론 하나만 확보해 제출해도 최소 5개 제한에 막히지 않는다."""
    rules = json.loads((PROJECT_ROOT/'data/case/inferences.private.json').read_text())['rules']
    rule = next(r for r in rules if r['phase']==1 and all(s['kind']=='evidence' for s in r['sources']))
    for source in rule['sources']:
        play.act('examinations', evidence_id=source['id'])
    play.act('inferences', sources=rule['sources'])
    ids = list(play.state['derivedEvidence'])
    assert len(ids)==1
    verdict = play.act('accusations', **selections(), evidence_ids=ids)['result']
    assert verdict['submittedEvidenceIds']==ids
    assert verdict['checks'][-1]['correct'] is False
````

## test_unearned_inference_still_rejected_without_consuming_state

[원본 56번째 줄](../../../tests/test_open_accusation.py#L56)

제출 자유가 존재하지 않는 추론을 근거로 제출할 권한까지 주지는 않는다.

### 입력과 처리

```python
def test_unearned_inference_still_rejected_without_consuming_state(api, game):
```

### 실제 코드

````python
def test_unearned_inference_still_rejected_without_consuming_state(api, game):
    """제출 자유가 존재하지 않는 추론을 근거로 제출할 권한까지 주지는 않는다."""
    response = api('POST', '/v1/games/'+game['game_id']+'/accusations', {
        'request_id':str(uuid4()), 'expected_revision':0, **selections(),
        'evidence_ids':['derived-reset-impact-fit']}, game['game_token'])
    assert response.status_code == 422
    state = api('GET', '/v1/games/'+game['game_id'], game_token=game['game_token']).json()['state']
    assert state['verdict'] is None
    assert state['revision']==0
````

