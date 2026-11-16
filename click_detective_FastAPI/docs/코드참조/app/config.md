# `app/config.py`

[코드 참조 목차](../README.md) · [전체 문서 목차](../../README.md) · [실제 소스](../../../app/config.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 97줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

프로젝트 기준 .env 설정. 실행 위치가 달라도 같은 데이터·모델을 사용한다.

## `Settings`

[소스 선언 위치](../../../app/config.py#L12)

```python
class Settings(BaseSettings):
    ...
```

실행 설정. local은 실제 모델, fixture는 GPU 없는 명시적 개발·테스트 모드다.

**파라미터**

- api_key (str): 서버 인증에 사용할 비밀 API 키.
- database_path (Path): 수사 상태와 요청 기록을 저장할 SQLite 파일 경로.
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
- generation_attempts (int): 최초 시도를 포함한 대사 생성 횟수 상한.
- verification_attempts (int): 같은 후보에 대해 배치별 보고서를 요청할 횟수 상한.
- verification_batch_size (int): 한 번의 검증 호출에서 확인할 승인 문장 수.
- rag_enabled (bool): 승인된 사실 안에서 관련성 검색을 수행할지 여부.
- rag_top_k (int): 필수 사실 외에 추가로 선택할 관련 사실 수의 상한.
- history_limit (int): 프롬프트에 담을 최근 대화 항목 수.
- diagnostics_enabled (bool): 대화 생성 진단을 파일에 기록할지 여부.
- diagnostics_path (Path): 대화 생성 진단 JSONL 파일 경로.

**반환값**

Settings: 위 역할을 수행하도록 생성된 객체.

## `Settings.project_path`

[소스 선언 위치](../../../app/config.py#L85)

```python
def project_path(cls, value):
    ...
```

상대 경로와 ~를 해석한다. 모델 파일은 자동 다운로드하지 않는다.

**파라미터**

- value: 절대 경로로 변환할 문자열·Path 또는 None.

**반환값**

Path | None: 프로젝트 기준 절대 경로. 입력이 None이면 None.
