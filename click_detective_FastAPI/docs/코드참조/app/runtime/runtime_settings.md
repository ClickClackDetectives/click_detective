# `app/runtime/runtime_settings.py`

[코드 참조 목차](../../README.md) · [도메인 목차](README.md) · [실제 소스](../../../../app/runtime/runtime_settings.py)

프로젝트 기준 .env 설정. 실행 위치가 달라도 같은 데이터·모델을 사용한다.

## `Settings`

[소스 선언](../../../../app/runtime/runtime_settings.py#L12)

```python
class Settings(BaseSettings):
    ...
```

실행 설정. local은 실제 모델, fixture는 GPU 없는 명시적 개발·테스트 모드다.

**인자**

- api_key (str): 서버 인증에 사용할 비밀 API 키.
- postgres_dsn: 계정과 세션을 저장하는 PostgreSQL 연결 문자열.
- auth_jwt_secret: 접근 토큰 서명에 사용하는 32바이트 이상의 비밀값.
- mongo_uri: 수사 저장용 MongoDB replica set 연결 문자열.
- mongo_database: 수사와 요청 기록을 저장할 MongoDB DB 이름.
- data_dir (Path): 사건 JSON 데이터가 있는 디렉터리.
- generation_mode (Literal['local', 'fixture']): local이면 실제 모델을 사용하고 fixture이면 고정 대사를 사용한다.
- local_model_path (Path): 로컬에 준비된 Qwen 모델 디렉터리.
- local_model_version (str): 생성 응답에 표시할 기본 모델 버전 이름.
- lora_adapter_path (Path | None): 기존 LoRA 어댑터 디렉터리. None이면 기본 모델만 사용한다.
- adapter_version (str): 응답 모델 버전에 덧붙일 어댑터 이름.
- generation_output_format (Literal['text', 'json']): 생성 모델에 요구할 출력 형식. text는 대사 원문, json은 JSON 객체다.
- max_input_tokens (int): 모델 입력으로 허용할 최대 토큰 수.
- max_new_tokens (int): 한 번의 모델 호출에서 새로 생성할 최대 토큰 수.
- dialogue_temperature (float): 대사 표현을 다양하게 선택하는 정도. 0이면 샘플링하지 않는다.
- dialogue_top_p (float): 대사 샘플링에서 선택 후보로 삼을 누적 확률 범위.
- dialogue_repetition_penalty (float): 생성 대사에서 같은 표현의 반복을 줄이는 계수.
- timeout_seconds (float): 그래프 전체와 모델 처리 단계에 적용할 초 단위 제한 시간.
- fallback_on_error (bool): 생성·검증 실패 시 승인 원문 대사로 복구할지 여부.
- verification_batch_size (int): 한 번의 검증 호출에서 확인할 승인 문장 수.
- rag_enabled (bool): 자유 질문의 E5 벡터 검색 사용 여부.
- rag_top_k (int): 자유 질문에서 고를 개별 진술 수의 상한.
- rag_min_score (float): 자유 질문에 적용하는 E5 코사인 유사도 하한.
- rag_embedding_dir (Path | None): E5 파일 경로. local 기본값은 models/retrieval.
- rag_bm25_enabled (bool): 유사도 기준을 통과한 후보의 Kiwi BM25 재정렬 사용 여부.
- rag_dense_weight (float): 가중 RRF에서 E5 순위에 줄 비중.
- rag_rrf_k (int): 가중 RRF에서 순위 분모에 더하는 상수.
- history_limit (int): 프롬프트에 담을 최근 대화 항목 수.
- diagnostics_enabled (bool): 대화 생성 진단을 파일에 기록할지 여부.
- diagnostics_path (Path): 대화 생성 진단 JSONL 파일 경로.
- agent_test_enabled (bool): 인증된 에이전트 단독 검사 API를 활성화할지 여부.
- validation_similarity_threshold: 검증 문장 후보를 거르는 유사도 기준.
- validation_similarity_backend: 검증 문장 임베딩 방식.
- validation_embedding_model: 로컬 경로나 캐시에 준비한 SentenceTransformer 모델 ID.
- validation_embedding_device: 임베딩 모델 실행 장치.

**반환값**

- Settings: 위 역할을 수행하도록 생성된 객체.

## `Settings.project_path`

[소스 선언](../../../../app/runtime/runtime_settings.py#L111)

```python
def project_path(cls, value):
    ...
```

상대 경로와 ~를 해석한다. 모델 파일은 자동 다운로드하지 않는다.

**인자**

- value: 절대 경로로 변환할 문자열·Path 또는 None.

**반환값**

- Path | None: 프로젝트 기준 절대 경로. 입력이 None이면 None.

## `Settings.empty_connection_setting`

[소스 선언](../../../../app/runtime/runtime_settings.py#L127)

```python
def empty_connection_setting(cls, value):
    ...
```

빈 연결 환경변수로 개발 프로세스의 계정 설정을 끌 수 있게 한다.

**인자**

- value: 연결 문자열·서명 키 또는 값을 생략한 입력.

**반환값**

- str | SecretStr | None: 빈 문자열을 None으로 바꾼 설정값.

## `Settings.require_account_storage`

[소스 선언](../../../../app/runtime/runtime_settings.py#L139)

```python
def require_account_storage(self):
    ...
```

계정 기능의 데이터베이스와 서명 키 설정 조합을 검사한다.

**인자**

- 없음.

**반환값**

- Settings: 검증된 실행 설정.
