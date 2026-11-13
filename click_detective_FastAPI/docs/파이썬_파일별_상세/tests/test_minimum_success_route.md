# tests/test_minimum_success_route.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../tests/test_minimum_success_route.py)

## 역할과 읽는 순서

현재 채점 하한 경로와 중요 쟁점까지 확보하는 경로를 실제 데이터·API로 비교한다.

테스트 파일은 실제 프로젝트 데이터를 사용하되 fixture와 모의 모델을 구분합니다. 테스트 통과는 GPU 품질의 독립 검증이 아닙니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## data

[원본 6번째 줄](../../../tests/test_minimum_success_route.py#L6)

프런트엔드가 아닌 백엔드 자체 사건 데이터를 읽는다.

### 입력과 처리

```python
def data(name):
```

### 실제 코드

````python
def data(name):
    """프런트엔드가 아닌 백엔드 자체 사건 데이터를 읽는다."""
    return json.loads((PROJECT_ROOT/'data/case'/name).read_text())
````

## infer

[원본 11번째 줄](../../../tests/test_minimum_success_route.py#L11)

현재 규칙에서 지정한 정확한 출처 조합으로 추론을 생성한다.

### 입력과 처리

```python
def infer(play, key):
```

### 실제 코드

````python
def infer(play, key):
    """현재 규칙에서 지정한 정확한 출처 조합으로 추론을 생성한다."""
    rule=next(rule for rule in data('inferences.private.json')['rules'] if rule['id']==key)
    play.act('inferences', sources=rule['sources'])
````

## prepare_shared_case

[원본 17번째 줄](../../../tests/test_minimum_success_route.py#L17)

두 경로에 공통인 4회 심문·14개 원본·핵심 선행 추론을 API로 마련한다.

### 입력과 처리

```python
def prepare_shared_case(play):
```

### 실제 코드

````python
def prepare_shared_case(play):
    """두 경로에 공통인 4회 심문·14개 원본·핵심 선행 추론을 API로 마련한다."""
    for key in ['1-02','1-08','1-13','S-K']:
        play.act('examinations', evidence_id=key)
    infer(play,'reset-debt-delay')
    play.act('interrogations',suspect_id='kang',question='와인잔에 무엇을 했나요?',material_id='1-02')
    play.act('interrogations',suspect_id='kang',question='채무와 약의 경위를 설명해 주세요.',material_id='derived-reset-debt-delay')
    infer(play,'reset-glass-entry')
    play.act('phase-transitions',target_phase=2)
    for key in ['1-01','1-03','1-10','2-02','2-08','2-04','2-07','S-S','2-11']:
        play.act('examinations',evidence_id=key)
    for suspect in ['cha','baek']:
        play.act('interrogations',suspect_id=suspect,question='그날 밤 면담 전후의 동선과 직접 본 일을 말씀해 주세요.',topic_id='movement')
    for key in ['reset-impact-fit','reset-observation-gap','reset-deadline-pressure','reset-disposal-materials']:
        infer(play,key)
````

## submit_core_accusation

[원본 34번째 줄](../../../tests/test_minimum_success_route.py#L34)

이미 생성한 다섯 핵심 추론을 제출해 채점과 종결을 확인한다.

### 입력과 처리

```python
def submit_core_accusation(play):
```

### 실제 코드

````python
def submit_core_accusation(play):
    """이미 생성한 다섯 핵심 추론을 제출해 채점과 종결을 확인한다."""
    answer=data('solution.private.json')['solution']
    ids=data('game-rules.json')['accusation']['requiredInferenceIds']
    return play.act('accusations',suspect_id=answer['suspectId'],motive=answer['motive'],method=answer['method'],evidence_ids=ids)['result']
````

## test_five_question_success_route

[원본 41번째 줄](../../../tests/test_minimum_success_route.py#L41)

5회 경로는 채점상 통과하지만 중요 쟁점 전체의 발견을 보장하지 않음을 비교한다.

### 입력과 처리

```python
def test_five_question_success_route(play):
```

### 실제 코드

````python
def test_five_question_success_route(play):
    """5회 경로는 채점상 통과하지만 중요 쟁점 전체의 발견을 보장하지 않음을 비교한다."""
    prepare_shared_case(play)
    play.act('interrogations',suspect_id='seo',question='태운 물품과 이유를 설명해 주세요.',material_id='derived-reset-disposal-materials')
    infer(play,'reset-record-concealment')
    assert play.state['questions']==5
    assert len(play.state['examined'])==14
    assert set(play.state['revealed'])=={'gang_drug','gang_visit','seo_burn'}
    assert len(play.state['derivedEvidence'])==7
    assert play.state['progress']['percent']==49
    verdict=submit_core_accusation(play)
    assert verdict['correct'] is True
    assert verdict['score']==100
````

## test_minimum_important_findings_route

[원본 56번째 줄](../../../tests/test_minimum_success_route.py#L56)

중요 쟁점 5개를 포함한 8회 심문·6개 쟁점·7개 추론의 입증 경로를 확인한다.

### 입력과 처리

```python
def test_minimum_important_findings_route(play):
```

### 실제 코드

````python
def test_minimum_important_findings_route(play):
    """중요 쟁점 5개를 포함한 8회 심문·6개 쟁점·7개 추론의 입증 경로를 확인한다."""
    prepare_shared_case(play)
    for suspect,key,question in [
        ('seo','derived-reset-deadline-pressure','위작과 진품 판매에 대해 설명해 주세요.'),
        ('seo','derived-reset-disposal-materials','태운 물품과 이유를 설명해 주세요.'),
        ('seo','derived-reset-impact-fit','흉기와 상처의 부합을 설명해 주세요.'),
        ('cha','derived-reset-disposal-materials','소각 시간대에 본 사람의 얼굴을 확인했나요?')]:
        play.act('interrogations',suspect_id=suspect,question=question,material_id=key)
    infer(play,'reset-record-concealment')
    assert play.state['questions']==8
    assert len(play.state['examined'])==14
    assert set(play.state['revealed'])=={'gang_drug','gang_visit','seo_forgery','seo_burn','weapon_fit','witness_gap'}
    assert len(play.state['derivedEvidence'])==7
    assert play.state['progress']['percent']==55
    verdict=submit_core_accusation(play)
    assert verdict['correct'] is True
    assert verdict['score']==100
````

