# Click Detective FastAPI

Click Detective는 증거를 열람하고 용의자를 심문해 사건을 해결하는 탐정 게임입니다. FastAPI는 공개 사건 자료, 계정, 수사 상태와 판정, 등장인물의 대사를 제공합니다. 플레이 화면과 브라우저 요청은 [Next.js 프로젝트](../click_detective_Next_js/README.md)에서 처리합니다.

## fixture로 시작하기

Python 3.11 이상과 MongoDB replica set을 준비합니다. fixture 모드에서도 수사 상태는 MongoDB에 저장됩니다. [MongoDB 설정](docs/서버/MongoDB_설치와_실행.md)

저장소 루트에서 실행합니다.

```bash
cd click_detective_FastAPI
python3 -m venv .click_venv
source .click_venv/bin/activate
python -m pip install -e '.[dev]'
cp -n .env.example .env
```

`.env`에서 `CLICK_GENERATION_MODE=fixture`로 바꾸고, `CLICK_MONGO_URI`에 준비한 replica set의 연결 문자열을 입력합니다. `CLICK_API_KEY`는 16자 이상의 서비스 키로 지정하고 Next.js 서버의 `CLICK_DETECTIVE_API_KEY`에도 같은 값을 설정합니다. 계정 기능까지 실행하려면 PostgreSQL 연결과 JWT 서명 키를 추가합니다. [계정과 수사 저장소](docs/시작하기/05_계정과_수사_저장소.md)

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
curl --fail http://127.0.0.1:8000/healthz
```

상태 확인에 성공하면 `{"status":"ok"}`가 반환됩니다. 브라우저에서 `http://127.0.0.1:8000/docs`를 열면 API를 탐색할 수 있습니다. 게임 API는 서비스 키를 Bearer 인증에 사용하고, 익명 수사 요청에는 `X-Game-Token`을, 계정 수사 요청에는 `X-Access-Token`을 함께 보냅니다. [API 인증과 요청 예시](docs/API/README.md)

## 로컬 모델로 실행하기

호환되는 NVIDIA GPU와 CUDA 환경에서 `python -m pip install -e '.[local,embeddings]'`를 실행합니다. Qwen 가중치와 토크나이저, 설정에 지정한 LoRA 어댑터, 자유 질문 검색용 E5 및 문장 검증용 SentenceTransformer 파일을 준비합니다. `CLICK_GENERATION_MODE=local`로 바꾸고 모델 경로를 실제 위치에 맞춘 뒤 같은 Uvicorn 명령으로 시작합니다. [모델 파일 배치](models/README.md) · [공용 모델 실행](docs/에이전트/공용_모델.md)

## 프로젝트 구조

```text
click_detective_FastAPI/
├── app/
│   ├── main.py                  # 앱 생성과 라우터 등록
│   ├── runtime/                 # 설정, 서비스 인증, lifespan
│   ├── auth/                    # 계정·세션·탈퇴
│   │   ├── controllers/         # 가입·로그인·세션·탈퇴 HTTP 요청
│   │   ├── dto/                 # 계정 요청·응답과 토큰 데이터 계약
│   │   ├── providers/           # 계정 서비스와 저장소 조립
│   │   ├── repositories/        # PostgreSQL 계정·세션 저장
│   │   └── services/            # 계정 인증, 토큰 발급, 탈퇴 처리
│   ├── cases/                   # 사건 버전·카탈로그·공개 자산
│   │   ├── controllers/         # 카탈로그·사건·공개 자산 HTTP 요청
│   │   ├── dto/                 # 공개 카탈로그 데이터 계약
│   │   ├── providers/           # 카탈로그 서비스와 저장소 조립
│   │   ├── repositories/        # 사건 원본·버전·자산 파일 접근
│   │   └── services/            # 공개 사건 목록과 상세 응답 구성
│   ├── investigation/           # 수사 규칙과 상태
│   │   ├── controllers/         # 수사·자료·화면 HTTP 요청
│   │   ├── dto/                 # 수사 명령과 심문 계획의 데이터 계약
│   │   ├── providers/           # 수사 의존성 조립
│   │   ├── repositories/        # MongoDB 저장, 예약과 상태 확정
│   │   └── services/
│   │       ├── investigation_game_service.py  # 수사 유스케이스
│   │       ├── interrogation/   # 공개 범위 확인과 심문 계획
│   │       ├── rules/           # 증거·진술·고발 규칙
│   │       └── views/           # 화면용 응답 구성
│   └── dialogue/                # 대사 생성과 검증
│       ├── controllers/         # 내부 에이전트 검사 API
│       ├── dto/                 # 대화 요청·응답과 그래프 상태
│       ├── providers/           # 모델과 대화 서비스 조립
│       ├── repositories/        # 검색 인덱스와 모델 파일 접근
│       └── services/
│           ├── reply/           # 대화 그래프와 응답 서비스
│           ├── preprocess_agent/
│           │   └── rag/         # 공개 가능한 진술 검색과 재정렬
│           ├── inference_agent/  # 후보 대사 생성
│           ├── validation_agent/ # 후보 문장과 승인 근거 대조
│           ├── model/           # 로컬 모델 로딩과 실행
│           └── diagnostics/     # 실행 시간과 판정 기록
├── data/                        # 사건 원본과 자산
├── models/                      # 로컬 모델 배치
├── scripts/                     # 실서버와 배치 검사
├── tests/                       # 회귀 테스트와 fixture
├── docs/                        # 개발·운영 문서
└── pyproject.toml               # Python 의존성과 검사 설정
```

[파일별 코드 참조](docs/코드참조/README.md) · [전체 처리 흐름](docs/시작하기/03_전체_처리_흐름.md)

## 사용 기술

| 기술 | 용도 |
| --- | --- |
| Python 3.11+, FastAPI, Uvicorn | 게임·계정 API 구현과 실행 |
| Pydantic, pydantic-settings | 요청·응답 데이터 검증과 환경 설정 |
| MongoDB replica set, PyMongo, MongoEngine | 수사 상태와 변경 요청 저장 |
| PostgreSQL, SQLAlchemy, psycopg | 계정과 세션 저장 |
| LangGraph | 심문 전처리·생성·검증 단계 연결 |
| Qwen2.5-7B-Instruct, PyTorch, Transformers, bitsandbytes, PEFT | 로컬 대사 생성·의미 검증, NF4 4비트 로딩과 LoRA 어댑터 적용 |
| multilingual-e5-small, ONNX Runtime, ChromaDB, Kiwi, BM25 | 자유 질문에 답할 수 있는 승인 진술 검색과 재정렬 |
| Sentence Transformers | 후보 대사와 승인 문장의 유사도 계산 |
| pytest, Ruff | 회귀 테스트, 정적 검사와 포맷 확인 |

[Python 의존성 설정](pyproject.toml)

## 개발 확인

```bash
python -m ruff check app scripts tests
python -m ruff format --check app scripts tests
python -m pytest -q
```

DB fixture와 실제 모델의 검사 절차를 확인하려면 [테스트 안내](docs/테스트/README.md)를 참고합니다. 설치, 운영, API, 코드 참조는 [문서 목차](docs/README.md)에서 찾을 수 있습니다.
