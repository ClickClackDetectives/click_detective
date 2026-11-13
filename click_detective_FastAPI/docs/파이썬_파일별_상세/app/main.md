# app/main.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../app/main.py)

## 역할과 읽는 순서

FastAPI 진입점. Next.js는 이 API의 공개 결과를 표시하고 게임 규칙을 실행하지 않는다.

FastAPI 경로 18개를 등록합니다. 인증 → 서비스 → 도메인·저장 순으로 연결하며, 모델은 lifespan의 local 모드에서만 로딩합니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## 모듈 설정과 상수

```python
bearer = HTTPBearer(auto_error=False)
app = create_app()
```

이 값은 코드 선언입니다. 실제 .env 비밀값이나 수사 DB 값은 여기에 읽어 넣지 않았습니다.

## authenticate

[원본 24번째 줄](../../../app/main.py#L24)

Next.js 서버 전용 API 키를 검사한다. 브라우저에 이 키를 전달하지 않는다.

### 입력과 처리

```python
async def authenticate(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
```

async 함수이므로 호출자는 await로 결과를 기다립니다. 대기 중 다른 요청이 실행될 수 있어 revision과 잠금 처리가 필요합니다.

주요 분기 조건은 `credentials is None or not hmac.compare_digest(credentials.credentials, request.app.state.settings.api_key)`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
async def authenticate(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    """Next.js 서버 전용 API 키를 검사한다. 브라우저에 이 키를 전달하지 않는다."""
    if credentials is None or not hmac.compare_digest(credentials.credentials, request.app.state.settings.api_key):
        raise HTTPException(401, "서비스 인증이 필요합니다.", headers={"WWW-Authenticate": "Bearer"})
````

## create_app

[원본 30번째 줄](../../../app/main.py#L30)

앱을 구성한다. 실제 데이터·DB·모델 준비는 lifespan에서 수행한다.

### 입력과 처리

```python
def create_app(settings: Settings | None = None):
```

주요 분기 조건은 `config.generation_mode == 'local'`, `not separator or kind not in {'evidence', 'testimony', 'derived'}`, `kind == 'evidence'`, `not name or not path.is_relative_to(svc.c.root / 'public') or (not path.is_file())`, `screen == 'evidence'`, `screen == 'testimonies'` 등입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def create_app(settings: Settings | None = None):
    """앱을 구성한다. 실제 데이터·DB·모델 준비는 lifespan에서 수행한다."""
    @asynccontextmanager
    async def lifespan(app):
        """정적 데이터와 모델은 한 번 로딩한다. fixture 모드에서만 GPU를 생략한다."""
        config = settings or Settings()
        catalog = Catalog(config.data_dir)
        engine = Engine(catalog)
        presenter = Presenter(catalog, engine)
        graph = None
        if config.generation_mode == "local":
            from .dialogue.local_model import LocalQwenModel
            from .dialogue.interrogation_graph import InterrogationGraph
            model = LocalQwenModel(config)
            await asyncio.to_thread(model.load)
            graph = InterrogationGraph(config, model)
        service = GameService(config, catalog, Repository(config.database_path), engine, Planner(catalog), presenter, graph)
        app.state.settings, app.state.service = config, service
        yield

    app = FastAPI(title="Click Detective", version="0.1.0", lifespan=lifespan,
                  description="사건 데이터·규칙·수사 저장·양자화 Qwen 대사 생성을 담당하는 백엔드")

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request, error):
        """원문·토큰을 오류 응답에 복사하지 않고 위치·오류 종류만 반환한다."""
        return JSONResponse(status_code=422, content={"detail": [{"loc": item["loc"], "type": item["type"]} for item in error.errors()]})

    @app.middleware("http")
    async def no_store(request, call_next):
        """수사별 데이터가 브라우저나 프록시의 공용 캐시에 남지 않게 한다."""
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    def service(request: Request):
        """공통 인증을 통과한 API에 게임 서비스를 제공한다."""
        return request.app.state.service

    def game(request: Request, game_id: str):
        """게임 토큰과 버전으로 접근 권한을 확인한다."""
        svc = service(request)
        return svc.read(game_id, request.headers.get("X-Game-Token", ""))

    async def mutate(request, game_id, command, action):
        """모든 변경 API가 같은 중복·revision·확정 경로를 사용한다."""
        return await service(request).change(game_id, request.headers.get("X-Game-Token", ""), command, action)

    @app.get("/healthz", tags=["운영"])
    async def health():
        """서버 시작 완료를 확인한다. 모델 품질 시험을 실행하지 않는다."""
        return {"status": "ok"}

    secured = [Depends(authenticate)]

    @app.get("/v1/catalog", dependencies=secured, tags=["사건"])
    async def catalog(request: Request):
        """초기 화면 데이터 전체를 공개 DTO로 반환한다."""
        return service(request).c.public_catalog()

    @app.get("/v1/cases", dependencies=secured, tags=["사건"])
    async def cases(request: Request):
        """실제로 시작 가능한 사건만 반환한다."""
        data = service(request).c
        return {"cases": [{"case_id": data.case_id, "scenario_version": data.version, **data.case["case"]}]}

    @app.get("/v1/cases/{case_id}", dependencies=secured, tags=["사건"])
    async def case_detail(case_id: str, request: Request):
        """사건 소개·인물·공개 콘텐츠를 반환한다. 비공개 규칙은 제외한다."""
        service(request).c.require_case(case_id)
        return service(request).c.public_catalog()

    @app.get("/v1/assets/{asset_path:path}", dependencies=secured, tags=["자산"])
    async def public_asset(asset_path: str, request: Request):
        """소개·인물 이미지·영상만 제공한다. 증거 이미지는 수사 권한 경로로 제공한다."""
        return FileResponse(service(request).c.public_asset(asset_path))

    @app.post("/v1/games", dependencies=secured, tags=["수사"])
    async def create_game(command: NewGame, request: Request):
        """새 수사를 만들고 게임 토큰을 발급한다. Next.js는 토큰을 HttpOnly 쿠키에 보관한다."""
        return service(request).create(command)

    @app.get("/v1/games/{game_id}", dependencies=secured, tags=["수사"])
    async def get_game(game_id: str, request: Request):
        """화면용 수사 상태·진행률·자료·타임라인·가능 행동을 집계한다."""
        return {"state": service(request).presenter.state(game(request, game_id))}

    @app.get("/v1/games/{game_id}/materials", dependencies=secured, tags=["자료"])
    async def materials(game_id: str, request: Request, kind: str | None = None, archive_kind: str | None = None,
                        search: str = "", place: str | None = None):
        """공개 가능한 목록을 백엔드에서 분류·검색한다. GET은 열람 처리하지 않는다."""
        rows = service(request).presenter.materials(game(request, game_id))
        return {"materials": [item for item in rows if (not kind or item["kind"] == kind)
            and (not archive_kind or item["archiveKind"] == archive_kind)
            and (not place or item.get("type") == place)
            and search.casefold() in " ".join(str(item.get(key, "")) for key in ("code", "title", "summary", "type")).casefold()]}

    @app.get("/v1/games/{game_id}/materials/{material_key}", dependencies=secured, tags=["자료"])
    async def material_detail(game_id: str, material_key: str, request: Request):
        """획득한 원본·진술·추론만 본문을 제공한다. 접두사로 ID 충돌을 구분한다."""
        state = game(request, game_id)
        kind, separator, key = material_key.partition(":")
        if not separator or kind not in {"evidence", "testimony", "derived"}:
            raise HTTPException(422, "자료 키를 확인하세요.")
        svc = service(request)
        svc.engine.readable_source(state, {"kind": kind, "id": key})
        if kind == "evidence":
            record = svc.c.evidence[key]
            return {"kind": kind, **{field: record[field] for field in ("id", "code", "title", "type", "time", "phase", "body")},
                    "illustration": f"/v1/games/{game_id}/evidence-assets/{key}"}
        return {"kind": kind, **state["statements" if kind == "testimony" else "derivedEvidence"][key]}

    @app.get("/v1/games/{game_id}/evidence-assets/{evidence_id}", dependencies=secured, tags=["자산"])
    async def evidence_asset(game_id: str, evidence_id: str, request: Request):
        """원본 자료의 이미지도 열람 조건을 확인한다. 사용자 파일 경로는 받지 않는다."""
        state = game(request, game_id)
        svc = service(request)
        svc.engine.readable_source(state, {"kind": "evidence", "id": evidence_id})
        name = svc.c.evidence[evidence_id].get("illustration", "").lstrip("/")
        path = (svc.c.root / "public" / name).resolve()
        if not name or not path.is_relative_to(svc.c.root / "public") or not path.is_file():
            raise HTTPException(404, "이미지를 찾을 수 없습니다.")
        return FileResponse(path)

    @app.get("/v1/games/{game_id}/findings", dependencies=secured, tags=["쟁점"])
    async def findings(game_id: str, request: Request):
        """이미 발견된 쟁점만 반환한다. 미발견 조건·정답 목록은 공개하지 않는다."""
        return {"findings": game(request, game_id)["findingDetails"]}

    @app.get("/v1/games/{game_id}/views/{screen}", dependencies=secured, tags=["화면"])
    async def screen_view(game_id: str, screen: str, request: Request, search: str = "",
                          place: str = "all", person: str = "all", category: str = "evidence"):
        """원본 Next.js 화면의 분류·검색을 서버에서 처리하고 표시 결과만 돌려준다."""
        state = game(request, game_id)
        svc = service(request)
        views = ScreenViews(svc.c, svc.presenter)
        if screen == "evidence":
            return views.evidence(state, search, place)
        if screen == "testimonies":
            return views.testimonies(state, search, person)
        if screen == "inference":
            return views.inference(state, search, category)
        raise HTTPException(404, "화면을 찾을 수 없습니다.")

    @app.post("/v1/games/{game_id}/examinations", dependencies=secured, tags=["자료"])
    async def examine(game_id: str, command: Examine, request: Request):
        """증거 열람을 한 번 확정한다."""
        return await mutate(request, game_id, command, "examine")

    @app.post("/v1/games/{game_id}/interrogations", dependencies=secured, tags=["심문"])
    async def interrogate(game_id: str, command: Interrogate, request: Request):
        """서버 승인 계획→LangGraph→대화·증언·쟁점 원자적 확정을 수행한다."""
        return await mutate(request, game_id, command, "interrogate")

    @app.post("/v1/games/{game_id}/inferences", dependencies=secured, tags=["추론"])
    async def infer(game_id: str, command: Infer, request: Request):
        """실제로 획득한 정확한 출처 조합으로 추론 문서를 만든다."""
        return await mutate(request, game_id, command, "infer")

    @app.post("/v1/games/{game_id}/phase-transitions", dependencies=secured, tags=["진행"])
    async def advance(game_id: str, command: Advance, request: Request):
        """조건을 충족했을 때만 2차 조사와 자동 자료를 공개한다."""
        return await mutate(request, game_id, command, "advance")

    @app.put("/v1/games/{game_id}/notes", dependencies=secured, tags=["메모"])
    async def notes(game_id: str, command: Notes, request: Request):
        """revision을 검사하여 메모를 저장한다."""
        return await mutate(request, game_id, command, "notes")

    @app.post("/v1/games/{game_id}/accusations", dependencies=secured, tags=["고발"])
    async def accuse(game_id: str, command: Accuse, request: Request):
        """진행 조건 없이 고발을 받아 선택과 근거를 채점한다. LLM이 정답을 판정하지 않는다."""
        return await mutate(request, game_id, command, "accuse")

    return app
````

