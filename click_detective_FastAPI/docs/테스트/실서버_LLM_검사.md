# LLM·양자화·멀티에이전트 API만 실서버로 검사하기

## 1. 무엇을 검사하는가

검증 대상은 **`POST /v1/games/{game_id}/interrogations`**입니다. 실제 local 서버에서는 이 API가 승인 계획 → LangGraph 전처리 → 양자화 Qwen 생성 → 검증 → 수사 저장으로 이어집니다.

사용할 파일은 `scripts/test_llm_api_live.py`입니다. 기존 pytest 전체 게임 검사나 Next.js 화면 검사를 실행하는 명령이 아닙니다. 스크립트가 서버·GPU 모델을 하나 더 시작하지 않으며 이미 켜진 서버에 HTTP 요청을 보냅니다. 서버가 제공하는 대사 생성 경로는 이 API 한 개이고, 각 에이전트별로 외부 HTTP API가 따로 있는 것은 아닙니다.

수사 생성과 자료 열람은 심문 입력을 마련하기 위한 준비 단계입니다. 준비 API까지 전혀 호출하지 않는다는 뜻은 아닙니다. 고발·노트·단계 전환·전체 게임 진행은 하지 않습니다.

## 2. 터미널 A: 실제 모델 서버 실행

백엔드 `.env`에서 모델·어댑터·API 키·진단 설정을 확인하세요. 파일 경로는 본인이 복사한 실제 모델과 어댑터를 가리켜야 합니다.

```dotenv
CLICK_GENERATION_MODE=local
CLICK_DIAGNOSTICS_ENABLED=true
CLICK_DIAGNOSTICS_PATH=.data/dialogue-traces.jsonl
```

`.env` 전체를 위 세 줄로 덮어쓰라는 의미가 아닙니다. 모델 경로와 기존 키 등은 그대로 필요합니다. local 로더는 CUDA·4-bit NF4·double quantization을 사용하며, 설정된 기존 어댑터를 추론용으로 적용합니다. 이 테스트는 학습을 수행하지 않습니다.

```bash
cd click_detective_FastAPI
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

모델 로딩과 서버 시작이 완료될 때까지 기다립니다. 이미 실제 서버가 실행 중이면 다시 띄울 필요가 없습니다. 설정을 변경했다면 해당 서버를 재시작해야 합니다. `활성화한 가상환경`에 실제 모델 의존성이 없는 환경은 [설치 안내](../시작하기/02_설치와_실행.md)를 먼저 확인하세요.

실행 대상 DB에는 **사례마다 새 테스트 수사**가 남습니다. 기존 수사를 수정하거나 삭제하지는 않습니다. 테스트 기록을 분리하고 싶으면 서버 시작 시 별도 DB 경로를 지정하세요. 스크립트는 실행 중인 서버의 DB를 임의로 바꾸지 않습니다.

## 3. 터미널 B: 가장 작은 실서버 검사

```bash
cd click_detective_FastAPI
python scripts/test_llm_api_live.py \
  --backend-url http://127.0.0.1:8000 \
  --case profile
```

짧은 자기소개 요청 한 번을 검사합니다. 준비 조회·생성·저장 복원 호출은 별도로 필요합니다. 먼저 작은 요청으로 실제 모델 연결과 응답을 확인한 다음 범위를 넓히면 됩니다.

API 키는 기본적으로 환경변수 `CLICK_API_KEY`, 없으면 프로젝트 `.env`의 같은 이름에서 읽습니다. `.env`의 생성 모드를 검사 클라이언트가 읽어 서버 실행 모드로 착각하지 않습니다. 실제 서버의 응답과 선택적 진단으로 확인합니다.

## 4. 기본 3가지 심문 검사

```bash
cd click_detective_FastAPI
python scripts/test_llm_api_live.py \
  --backend-url http://127.0.0.1:8000
```

| 사례     | 구성                                                           | 확인 의도                  |
| -------- | -------------------------------------------------------------- | -------------------------- |
| profile  | 카탈로그 첫 인물에게 자기소개                                  | 짧은 승인 정보 생성·검증   |
| movement | 카탈로그 동선 주제의 질문                                      | 여러 승인 문장의 생성·검증 |
| evidence | 내부 실제 사건 데이터의 1차 단일 근거 쟁점 선택·자료 열람·제시 | 승인된 인정 대사·쟁점 저장 |

현재 데이터 기준 profile과 movement는 카탈로그 순서상 윤재혁, evidence는 처음 발견되는 단일 근거 항목에 따라 강민호의 재방문 자료를 사용합니다. 스크립트는 `data/case/evidence.json`, `findings.private.json`과 서버 카탈로그를 읽어 구성합니다. 서버와 클라이언트의 사건 데이터가 서로 다른 환경이면 `--data-dir`로 맞는 사본을 지정하세요.

각 사례는 독립된 새 수사를 사용합니다. 기본 대상 심문 요청은 3개지만 생성 재시도·문장 검증 배치 때문에 **내부 모델 호출 횟수는 3회보다 많을 수 있습니다.**

특정 사례만 여러 개 고를 수도 있습니다.

```bash
python scripts/test_llm_api_live.py \
  --case profile --case evidence
```

## 5. NF4와 세 에이전트 실행 진단까지 필수로 확인

같은 서버가 이 컴퓨터의 진단 JSONL에 쓰고 있다면 다음 명령을 사용합니다.

```bash
cd click_detective_FastAPI
python scripts/test_llm_api_live.py \
  --backend-url http://127.0.0.1:8000 \
  --case profile \
  --trace-path .data/dialogue-traces.jsonl \
  --require-trace
```

스크립트는 해당 심문의 request_id와 일치하는 기록만 찾습니다. 다음 두 묶음을 함께 확인합니다.

- `generation_mode=local`이며 retrieval·generation·verification 이벤트가 있음: 전처리 검색·생성·검증 호출 경로의 증거
- model_resources에 `loaded_in_4bit=true`, `quantization=nf4-double`이 있음: 그 요청에서 서버가 기록한 실제 모델 양자화 상태

`--require-trace`를 켜면 이 증거가 부족해도 실패입니다. `--trace-path`만 사용하면 참고 정보를 붙이고 진단 부족 자체를 필수 실패 조건으로 만들지는 않습니다.

원격 서버의 진단 파일은 로컬 기본 경로에 자동으로 생기지 않습니다. 같은 실행 서버의 진단 파일에 접근할 수 있어야 합니다. 오래된 다른 요청 기록으로 성공 처리하지 않습니다. 진단이 꺼져 있거나 경로가 틀리면 확인하지 못합니다.

HTTP만 검사한 경우 보고서 양자화 상태는 `not_measured_via_http`입니다. 모델 버전 이름에 `nf4`가 들어 있다는 이유만으로 양자화 자체를 입증하지 않습니다. 진단을 연결하고 모두 확인하면 `nf4_observed_in_server_runtime_trace`입니다.

## 6. 성공 조건

HTTP 200 외에도 다음을 확인합니다.

- request_id가 요청과 일치함
- finish_reason이 **stop**임
- 모델 버전이 비어 있지 않고 fixture·fixed·mock 이름이 아님
- 실제 reply와 used_fact_ids가 있음
- 질문 수가 정확히 한 번 증가함
- revision이 증가하고 질문/답변 쌍이 추가됨
- result.reply와 저장된 마지막 대사가 일치함
- 다시 GET한 상태가 변경 응답 상태와 같음
- evidence 사례는 선택한 쟁점이 실제 기록됨

`fixed`, `fallback`, `click-fixture-v1` 응답은 HTTP가 200이어도 실패입니다. 승인 사실이 없는 중립 응답 경로를 실수로 검사하지 않도록 실제 승인 사실이 있는 입력을 사용합니다.

응답 기반 판정은 테스트 대상 서버를 신뢰한다는 전제입니다. 버전 문자열만으로 악의적 모의 서버까지 구별하는 도구는 아닙니다. 원격 서버의 모델 내부를 직접 검사하는 관리 API를 추가한 것도 아닙니다.

기대 모델·어댑터 버전까지 정확히 비교하려면 서버의 실제 보고 이름을 지정하세요.

```bash
python scripts/test_llm_api_live.py \
  --case profile \
  --expected-model-version 'Qwen2.5-7B-Instruct-nf4+내_어댑터_버전'
```

이 값은 설명용입니다. 실제 `CLICK_LOCAL_MODEL_VERSION`과, 적용 시 더해지는 `+CLICK_ADAPTER_VERSION`에 맞춰야 합니다. 어댑터 적용 여부는 진단 record의 model_resources.adapter_enabled도 참고할 수 있습니다.

## 7. 입력·출력 JSON 보고서

기본 저장 위치는 `.reports/llm-api-live.json`이며 같은 경로로 실행하면 덮어씁니다. 보관하려면 `--report`로 다른 JSON 파일 이름을 지정하세요.

```bash
python scripts/test_llm_api_live.py \
  --case profile \
  --report .reports/llm-profile-live.json
```

| 필드                       | 내용                                               |
| -------------------------- | -------------------------------------------------- |
| mode                       | live_http, 실제 실행 서버를 호출했다는 의미        |
| target_api                 | 검사 대상 심문 API                                 |
| preparation                | 공통 healthz·catalog 왕복                          |
| cases                      | 사례별 요청·응답·조건·성공 여부                    |
| cases[].request_id         | 해당 심문 요청 UUID                                |
| cases[].exchanges[].input  | 메서드·경로·마스킹된 헤더·실제 본문                |
| cases[].exchanges[].output | HTTP 상태·전체 JSON 응답·생성 오류 코드            |
| elapsed_ms                 | 해당 HTTP 왕복 시간                                |
| cases[].checks             | 응답·저장 검증별 true/false                        |
| cases[].trace              | 선택적으로 연결한 같은 요청의 실행 진단            |
| quantization               | HTTP만 확인했는지, 서버 NF4 실행 진단도 확인했는지 |
| passed                     | 전체 성공 여부                                     |

API 키·수사 토큰은 필드와 문자열에서 마스킹합니다. 파일 권한은 소유자 읽기·쓰기인 600으로 저장합니다. 대사·수사 상태·자료 내용은 보고서에 남으므로 공유할 때 내용을 확인하세요.

## 8. 오류와 대기시간

기본 HTTP 대기시간은 요청마다 240초입니다. `--timeout 300`으로 바꿀 수 있지만 서버 내부 생성 제한시간을 늘리는 옵션은 아닙니다.

기본 플레이는 생성 실패를 200 fallback으로 복구합니다. strict 설정 등에서 502가 반환되면 output.generation_error를 확인하세요. `invalid_verification_output`, `pipeline_timeout` 등 실제 코드와 질문·UUID를 함께 남깁니다. fixture 서버라면 fixed 응답 조건에서 실패합니다. 401이면 API 키를, 409이면 버전 또는 서버 기록을 확인합니다.

타임아웃은 서버가 실제로 확정했는지 알 수 없는 상태입니다. 스크립트는 자동으로 새 UUID를 만들어 질문을 재전송하지 않습니다. 보고서의 UUID와 서버 진단으로 확인하세요. 재실행은 새로운 독립 수사를 생성하며 이전 타임아웃 요청의 재시도가 아닙니다.

종료 코드는 성공 0, 사례·준비 실패 1, CLI 설정 오류 2입니다. 설정 자체가 잘못되어 시작하지 못한 경우에는 실행 보고서가 생성되지 않을 수 있습니다.

## 9. 옵션과 코드 위치

```bash
python scripts/test_llm_api_live.py --help
```

주요 옵션은 `--backend-url`, 반복 가능한 `--case`, `--timeout`, `--report`, `--env-file`, `--api-key-env`, `--data-dir`, `--expected-model-version`, `--trace-path`, `--require-trace`입니다. API 키를 평문 CLI 인수로 받는 옵션은 없습니다. HTTP 프록시 환경변수는 자동 사용하지 않습니다.

도구 자체의 자동 검사는 `tests/live_dialogue/`입니다. 모의 HTTP·임시 FastAPI·가짜 응답으로 판정과 마스킹을 검사하며, 이 pytest 성공이 실제 모델 추론 성공은 아닙니다.

```bash
python -m pytest -q tests/live_dialogue/
```

## 플레이 응답과 엄격한 LLM 품질 검사의 구분

플레이 기본값 CLICK_FALLBACK_ON_ERROR=true에서는 모델 실패에도 승인 원문으로 답합니다. 사용자는 200과 대사를 받지만, 이 검사 도구는 여전히 fallback을 실제 모델 성공으로 세지 않습니다. 따라서 UI 정상 응답과 실서버 LLM 품질 검사 실패가 동시에 관찰될 수 있습니다. stop·fixed·fallback을 구분해 읽으세요. 별도 모델 진단 서버에서 오류 자체를 관찰하려면 false를 명시할 수 있습니다.

현재 기본값과 strict 검사의 차이, 복구 대화의 질문 차감은 [질문 응답 정책](../에이전트/응답과_복구_정책.md)을 참고하세요. fallback으로 사용자에게 답을 제공한 결과를 실제 모델 stop 성공으로 합산하지 않습니다.
