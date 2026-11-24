# Click Detective — FastAPI

## 개요

Click Detective(딸깍탐정단)는 증거를 조사하고 용의자를 심문하며 사건을 해결하는 웹 기반 탐정 게임입니다. 이 프로젝트는 사건 데이터, 수사 상태, 게임 규칙, 저장 및 AI 대사 생성을 담당하는 FastAPI 백엔드입니다. 화면은 별도 프로젝트인 `click_detective_Next_js`가 제공합니다.

## 프로젝트 소개

- 사건·인물·공개 이미지 및 영상 조회
- 증거 열람, 용의자 심문, 증언·쟁점 수집과 자료 조합 추론
- 조사 단계 전환, 진행률 계산, 고발 결과 판정
- SQLite 기반 수사 상태 및 메모 저장
- LangGraph 기반 대사 전처리·생성·검증과 승인된 사실 검색(RAG)
- 로컬 Qwen2.5-7B-Instruct의 NF4 4비트 로딩 및 기존 LoRA 어댑터 적용

게임 규칙과 정답 판정은 백엔드가 처리하고 LLM은 캐릭터 대사를 생성합니다. 모델을 새로 학습하지 않습니다.

**로컬 LLM 모델 가중치와 QLoRA로 학습된 LoRA 어댑터는 이 프로젝트에 포함되어 있지 않습니다.** 실제 LLM을 사용하려면 사용자가 모델과 해당 모델에 호환되는 학습된 어댑터를 별도로 준비해야 합니다. 모델·어댑터 없이 기능을 확인하려면 `fixture` 모드를 사용할 수 있습니다.

## 기술 스택

| 구분 | 기술 |
| --- | --- |
| 언어 | Python 3.11 이상 |
| API 서버 | FastAPI, Uvicorn |
| 설정·검증 | Pydantic, pydantic-settings |
| 저장소 | SQLite |
| 대화 워크플로 | LangGraph |
| 로컬 LLM | Qwen2.5-7B-Instruct, PyTorch, Transformers |
| 양자화·어댑터 | bitsandbytes(NF4), PEFT(LoRA), Accelerate |
| 테스트 | pytest, pytest-asyncio, HTTPX |

의존성 범위는 `pyproject.toml`에서 확인할 수 있습니다.

## 설치 및 실행 방법

아래 명령은 두 프로젝트의 상위 폴더에서 시작하는 Linux/macOS Bash 환경 기준입니다.

### 1. 의존성 설치

Python 3.11 이상을 준비합니다.

```bash
cd click_detective_FastAPI
python3 -m venv .cd_venv
source .cd_venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

### 2. 환경변수 설정

처음 설치할 때 예제 파일을 복사합니다. 기존 `.env`가 있다면 직접 수정합니다.

```bash
cp -n .env.example .env
```

`.env`에 다음 값을 설정합니다.

```dotenv
CLICK_API_KEY=replace-with-a-long-random-service-key
CLICK_GENERATION_MODE=fixture
```

`CLICK_API_KEY`는 16자 이상의 서비스 키로 변경합니다. Next.js의 `CLICK_DETECTIVE_API_KEY`에도 같은 값을 지정하며, 브라우저 코드나 `NEXT_PUBLIC_` 변수에 넣지 않습니다.

| 변수 | 설명 |
| --- | --- |
| `CLICK_API_KEY` | 서버 간 API 인증 키 |
| `CLICK_GENERATION_MODE` | `fixture`: GPU 없는 확인 / `local`: 실제 모델 사용 |
| `CLICK_DATABASE_PATH` | DB 경로, 기본값 `./.data/games.sqlite3` |
| `CLICK_DATA_DIR` | 사건 데이터 경로, 기본값 `./data` |
| `CLICK_LOCAL_MODEL_PATH` | 로컬 모델 경로 |
| `CLICK_LORA_ADAPTER_PATH` | 기존 LoRA 어댑터 경로 |
| `CLICK_RAG_EMBEDDING_DIR` | E5 모델 디렉터리. local 기본 경로는 `./models/retrieval` |
| `CLICK_RAG_TOP_K` | 자유 질문의 개별 진술 검색 결과 상한. 기본 3. 전체 동선 묶음은 한 후보로 검색 |
| `CLICK_RAG_MIN_SCORE` | ChromaDB에서 검색한 E5 벡터의 코사인 유사도 하한. 기본 0.8322 |
| `CLICK_RAG_BM25_ENABLED` | Kiwi BM25 재정렬 사용 여부. 기본 `true`. `false`이면 ChromaDB E5 순위를 사용 |
| `CLICK_RAG_DENSE_WEIGHT` | 가중 RRF에서 E5 순위의 비중. 기본 0.65. BM25 비중은 나머지 0.35 |
| `CLICK_RAG_RRF_K` | 가중 RRF의 순위 상수. 기본 40 |

상대 경로는 백엔드 프로젝트 폴더를 기준으로 해석됩니다. 설정 변경 후 서버를 재시작합니다.

### 3. GPU 없이 실행

가상환경을 활성화한 상태에서 실행합니다.

```bash
CLICK_GENERATION_MODE=fixture python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

`fixture`는 실제 LLM 대신 원문을 조립하는 개발·테스트 모드로, 게임 흐름과 저장·화면 연결을 확인할 수 있습니다.

GPU 없이 자유 질문의 하이브리드 검색까지 확인하려면 `python -m pip install -e '.[retrieval]'`을 실행하고 `CLICK_RAG_EMBEDDING_DIR=./models/retrieval`을 설정합니다. 이 설정이 없는 fixture는 기존 테스트용 진술 선택을 사용합니다.

- 상태 확인: http://127.0.0.1:8000/healthz — 정상 응답 `{"status":"ok"}`
- Swagger API 문서: http://127.0.0.1:8000/docs

게임 API는 Bearer 인증을 사용합니다. Swagger의 Authorize에 `CLICK_API_KEY`를 입력하며, 수사별 요청에는 별도 게임 토큰도 필요합니다.

### 4. 실제 로컬 LLM 실행

호환되는 NVIDIA GPU·드라이버와 CUDA 환경을 준비하고 로컬 모델 의존성을 설치합니다. PyTorch는 사용하는 CUDA 환경과 호환되어야 합니다.

```bash
python -m pip install -e '.[local]'
```

프로젝트에 포함되지 않은 다음 파일을 사용자가 직접 준비합니다. 서버는 모델이나 어댑터를 자동으로 다운로드하거나 학습하지 않습니다.

- **로컬 LLM 모델**: Qwen2.5-7B-Instruct 모델 가중치와 토크나이저 파일
- **QLoRA 어댑터**: 해당 기본 모델에 호환되는, QLoRA로 학습된 LoRA 어댑터 파일(`adapter_config.json`, `adapter_model.safetensors` 등)
- **자유 질문 검색 모델**: [multilingual-e5-small ONNX](https://huggingface.co/intfloat/multilingual-e5-small/tree/main/onnx)의 `model_qint8_avx512_vnni.onnx`를 `e5.onnx`로 저장하고 같은 폴더의 `tokenizer.json`을 함께 배치합니다.

준비한 파일을 아래 위치에 배치하거나 `.env`에 실제 저장 경로를 지정합니다.

```text
models/Qwen2.5-7B-Instruct/   # 모델·토크나이저 파일
adapters/best_adapter/       # adapter_config.json, adapter_model.safetensors 등
models/retrieval/           # e5.onnx, tokenizer.json
```

`.env`에 실제 경로를 설정합니다.

```dotenv
CLICK_GENERATION_MODE=local
CLICK_LOCAL_MODEL_PATH=./models/Qwen2.5-7B-Instruct
CLICK_LORA_ADAPTER_PATH=./adapters/best_adapter
```

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

모델 로딩과 서버 시작이 완료된 후 Next.js를 실행합니다. 모델이나 설정된 어댑터가 없으면 시작에 실패합니다. 파일 구성은 `models/README.md`, `adapters/README.md`를 참고하세요.

자유 질문과 진술을 E5로 벡터화하고 ChromaDB에서 코사인 거리로 검색합니다. ChromaDB는 백엔드 프로세스의 메모리에서 실행되며, 요청에 필요한 진술 벡터와 ID를 처음 검색할 때 저장합니다. 서버를 다시 띄우면 컬렉션이 새로 만들어집니다. 매 요청은 현재 인물과 공개 쟁점에서 승인된 ID로 검색을 제한합니다.

개별 동선과 공개된 인정 진술은 제목·시각·본문을 한 문자열로 만들어 임베딩합니다. 시각 정보가 없으면 제목과 본문을 사용합니다. ChromaDB 거리는 `1 - 거리`로 변환합니다. 질문에 적힌 정확한 시각은 원문의 시간 정보와 대조합니다. 개별 진술 후보에는 유사도 하한과 시각 조건을 통과한 1위 후보와의 유사도 차이 `0.02`를 적용합니다.

Kiwi는 질문과 공개 가능한 개별 진술에서 형태소를 추출합니다. BM25가 형태소가 겹치는 진술의 순위를 매기고, 가중 RRF가 E5와 BM25의 순위를 조합합니다. 이 순서로 유사도 조건을 통과한 후보에서 최대 `CLICK_RAG_TOP_K`개를 고릅니다. 전체 동선 후보가 유사도 기준을 통과해 1위라면 동선 묶음을 사용합니다.

생성과 수사 기록에는 승인된 원문을 사용합니다. 벡터 검색 결과가 없으면 고정 대사를 반환합니다. 명시적으로 선택한 주제와 증거로 새로 열린 인정 진술은 서버 규칙으로 처리합니다. `CLICK_RAG_ENABLED=false`로 설정하면 기존 선택 경로를 사용합니다.

## 테스트 및 추가 문서

전처리·생성·검증 에이전트별 구조와 코드 읽는 순서는 [코드 구조 안내](docs/시작하기/04_코드_읽는_순서.md)를 참고하세요. 각 Python 파일은 docstring을 포함하여 250줄 이내이며, 클래스·함수에 파라미터와 반환값 설명을 작성했습니다.

```bash
python -m pytest -q
python -m ruff check app scripts tests
python -m ruff format --check app scripts tests
```

테스트는 fixture·모의 모델 기반입니다. 실제 모델 검증은 `docs/테스트/실서버_LLM_검사.md`를 참고하세요.

- 전체 문서: `docs/README.md`
- 설치·설정 상세: `docs/시작하기/02_설치와_실행.md`
- API별 역할: `docs/API/상세/README.md`
- LLM 구조: `docs/에이전트/README.md`

기존 상세 문서의 `click_detective`는 현재 `click_detective_FastAPI`에 해당합니다. 수집 조건·최소 통과 조건 문서에는 사건 정답이 포함되어 있습니다.
