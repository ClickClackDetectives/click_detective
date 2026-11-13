# app/service.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../app/service.py)

## 역할과 읽는 순서

HTTP와 게임 엔진·모델·원자적 저장을 조정한다. 게임 판정은 전부 Python이 담당한다.

예약 → 규칙/생성 → 확정을 조정합니다. 기본 생성 오류는 승인 원문으로 복구합니다. 인증·revision·종결 조건은 생성 복구 범위 밖입니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## 모듈 설정과 상수

```python
logger = logging.getLogger(__name__)
```

이 값은 코드 선언입니다. 실제 .env 비밀값이나 수사 DB 값은 여기에 읽어 넣지 않았습니다.

## GameService

[원본 11번째 줄](../../../app/service.py#L11)

수사 생성·조회·변경과 GPU 대사를 연결한다.

## GameService.__init__

[원본 14번째 줄](../../../app/service.py#L14)

공용 객체를 연결한다. 모델은 서버 시작 시 한 번만 준비한다.

### 입력과 처리

```python
def __init__(self, settings, catalog, repository, engine, planner, presenter, graph=None):
```

### 실제 코드

````python
def __init__(self, settings, catalog, repository, engine, planner, presenter, graph=None):
        """공용 객체를 연결한다. 모델은 서버 시작 시 한 번만 준비한다."""
        self.settings, self.c, self.repo = settings, catalog, repository
        self.engine, self.planner, self.presenter, self.graph = engine, planner, presenter, graph
````

## GameService.read

[원본 19번째 줄](../../../app/service.py#L19)

소유권과 사건 버전을 검사해 저장 상태를 복원한다.

### 입력과 처리

```python
def read(self, game_id, token):
```

주요 분기 조건은 `state['scenarioVersion'] != self.c.version`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def read(self, game_id, token):
        """소유권과 사건 버전을 검사해 저장 상태를 복원한다."""
        state = self.repo.get(game_id, token)
        if state["scenarioVersion"] != self.c.version:
            raise HTTPException(409, "scenario_version_conflict")
        return state
````

## GameService.create

[원본 26번째 줄](../../../app/service.py#L26)

실행 가능한 사건·버전을 확인하고 생성 중복을 처리한다.

### 입력과 처리

```python
def create(self, command):
```

주요 분기 조건은 `command.scenario_version != self.c.version`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def create(self, command):
        """실행 가능한 사건·버전을 확인하고 생성 중복을 처리한다."""
        self.c.require_case(command.case_id)
        if command.scenario_version != self.c.version:
            raise HTTPException(409, "scenario_version_conflict")
        return self.repo.create(command, self.engine.initial, self.presenter.state)
````

## GameService.dialogue_request

[원본 33번째 줄](../../../app/service.py#L33)

저장 상태와 승인 계획에서 모델 DTO를 만든다. 외부 임의 승인 사실을 받지 않는다.

### 입력과 처리

```python
def dialogue_request(self, state, command, plan):
```

### 실제 코드

````python
def dialogue_request(self, state, command, plan):
        """저장 상태와 승인 계획에서 모델 DTO를 만든다. 외부 임의 승인 사실을 받지 않는다."""
        person = self.c.people[plan.suspect_id]
        return CharacterReplyRequest(request_id=command.request_id, game_id=state["id"], case_id=self.c.case_id,
            scenario_version=self.c.version, state_revision=state["revision"], turn_index=state["questions"] + 1,
            suspect_id=plan.suspect_id, phase=state["phase"], question=plan.question, topic_id=plan.topic,
            persona={"name": person["name"], "role": person["role"], "speech_style": "존댓말. 승인 원문의 말투와 관찰 한계를 유지하세요."},
            allowed_facts=plan.facts, required_fact_ids=[fact["id"] for fact in plan.facts],
            history=[{"role": message["role"], "text": message["text"]} for message in state["messages"]
                     if message["suspectId"] == plan.suspect_id][-self.settings.history_limit:] if self.settings.history_limit else [])
````

## GameService.reply

[원본 44번째 줄](../../../app/service.py#L44)

쟁점 유무와 무관하게 대사를 준비하고 모델 실패는 승인 원문으로 복구한다.

생성 대사를 검증 없이 통과시키지 않는다. 복구 대사는 서버가 승인한 사실만
사용하므로 원래 쟁점·증언 계획을 안전하게 확정할 수 있다. strict 설정에서는
오류를 그대로 전달하여 모델 품질 검사에 사용할 수 있다.

### 입력과 처리

```python
async def reply(self, request):
```

async 함수이므로 호출자는 await로 결과를 기다립니다. 대기 중 다른 요청이 실행될 수 있어 revision과 잠금 처리가 필요합니다.

주요 분기 조건은 `self.settings.generation_mode == 'fixture'`, `not self.settings.fallback_on_error`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
async def reply(self, request):
        """쟁점 유무와 무관하게 대사를 준비하고 모델 실패는 승인 원문으로 복구한다.

        생성 대사를 검증 없이 통과시키지 않는다. 복구 대사는 서버가 승인한 사실만
        사용하므로 원래 쟁점·증언 계획을 안전하게 확정할 수 있다. strict 설정에서는
        오류를 그대로 전달하여 모델 품질 검사에 사용할 수 있다.
        """
        if self.settings.generation_mode == "fixture":
            return CharacterReplyResponse(request_id=request.request_id, suspect_id=request.suspect_id,
                state_revision=request.state_revision, reply=assemble_reply(request),
                used_fact_ids=[fact.id for fact in request.allowed_facts],
                model_version="click-fixture-v1", finish_reason="fixed")
        try:
            response = await self.graph.generate(request)
            validate_generation(request, response, require_verbatim=response.finish_reason != "stop")
            return response
        except Exception as error:
            # 이 범위는 승인 계획 이후의 생성·검증만 감싼다. 인증·버전·게임 조건
            # 오류나 취소 신호(asyncio.CancelledError)는 성공 응답으로 바꾸지 않는다.
            if not self.settings.fallback_on_error:
                raise
            logger.warning("Dialogue recovered with approved facts: error_type=%s status=%s",
                           type(error).__name__, getattr(error, "status_code", None))
            response = CharacterReplyResponse(request_id=request.request_id, suspect_id=request.suspect_id,
                state_revision=request.state_revision, reply=assemble_reply(request),
                used_fact_ids=[fact.id for fact in request.allowed_facts],
                model_version=FIXED_MODEL_VERSION, finish_reason="fallback")
            validate_generation(request, response)
            return response
````

## GameService.change

[원본 74번째 줄](../../../app/service.py#L74)

짧은 예약→규칙·생성→짧은 확정. 중간 실패는 질문·쟁점·revision을 소비하지 않는다.

### 입력과 처리

```python
async def change(self, game_id, token, command, action):
```

async 함수이므로 호출자는 await로 결과를 기다립니다. 대기 중 다른 요청이 실행될 수 있어 revision과 잠금 처리가 필요합니다.

주요 분기 조건은 `'cached' in reservation`, `action == 'examine'`, `action == 'infer'`, `action == 'advance'`, `action == 'notes'`, `action == 'accuse'` 등입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
async def change(self, game_id, token, command, action):
        """짧은 예약→규칙·생성→짧은 확정. 중간 실패는 질문·쟁점·revision을 소비하지 않는다."""
        reservation = self.repo.reserve(game_id, token, command, action, self.settings.timeout_seconds * 2 + 30)
        if "cached" in reservation:
            return reservation["cached"]
        try:
            state = reservation["state"]
            self.engine.require_active(state)
            if action == "examine":
                result = self.engine.examine(state, command)
            elif action == "infer":
                result = self.engine.infer(state, command)
            elif action == "advance":
                result = self.engine.advance(state, command)
            elif action == "notes":
                state["notes"] = command.text
                result = {"saved": True}
            elif action == "accuse":
                result = self.engine.accuse(state, command)
            elif action == "interrogate":
                plan = self.planner.prepare(state, command)
                request = self.dialogue_request(state, command, plan)
                response = await self.reply(request)
                result = self.engine.record_plan(state, plan, response)
            else:
                raise HTTPException(404, "행동을 찾을 수 없습니다.")
            return self.repo.commit(game_id, command, reservation, state, result, self.presenter.state)
        finally:
            self.repo.abort(command, reservation)
````

