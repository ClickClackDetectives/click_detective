# FastAPI 작업 규칙

## 파일 배치

- `cases`는 사건 원본, 버전, 공개 카탈로그·자산을 담당한다. `investigation`은 게임 규칙, 질문·자료 승인, 수사 상태와 MongoDB 저장을 담당한다. 계정 저장은 `app/auth/repositories/auth_repository.py`의 PostgreSQL 경로를 사용한다. `dialogue`는 승인된 문맥의 RAG·프롬프트, 그래프, 응답 파싱, 승인 문장 판정·부분 응답·복구를 담당한다.
- 이관 대상 도메인에는 `controllers/`, `services/`, `dto/`, `repositories/`, `providers/`를 둔다. 빈 계층에는 `__init__.py`를 두고 기능 파일은 `<도메인>_<기능>.py`로 이름을 짓는다. HTTP 처리는 컨트롤러, 유스케이스와 규칙·화면 데이터 조립은 서비스, 계약은 DTO, 파일·DB 접근은 저장소, 객체 조립은 provider에 둔다.
- 이관 전 경로를 수정할 때는 실제 호출부를 따라간다. 예를 들어 수사 도메인의 기존 `api/`, `service.py`, `rules/`, `views/`, `persistence/`를 확인한다. 이관 작업에서는 호출부와 테스트를 함께 갱신하고 검증한 뒤 이전 경로를 정리한다.
- 앱 진입점 `app.main:app`과 `create_app()`을 유지한다. 공통 설정·서버 간 인증·lifespan은 `app/runtime/`에서 관리한다. 계정 인증은 `app/auth/`에서 관리한다. provider가 의존성을 조립하고, 도메인 간 호출에는 공개 서비스와 DTO를 사용한다.

## 유지할 계약

- 공개 경로·응답·오류와 인증, 기존 증거 열람 조건, `GET/POST /internal/agent-test`의 인증·활성화 조건·응답을 유지한다. 사건 공개 응답은 기존 공개 필드로 제한한다.
- 상태 변경의 요청 식별자·revision 검증과 예약 → 처리 → 확정 흐름을 유지한다. 실패 시 예약을 해제하고 저장된 수사 재개와 재시도를 검증한다.
- 기존 검증 구현이 쓰는 공유 심볼과 의존성을 먼저 이관한다. 기존 검증 버전별 동작과 진단 계약을 확인한 뒤 이전 검증 구현을 정리한다. 삭제 후보는 라우터·DI·fixture·동적 import와 운영 스크립트·노트북의 참조도 확인한다.
- `ReplyModel`과 로컬 모델 실행은 단일 FastAPI의 `app/dialogue/`에 둔다. `model_loading.py`에서 모델·토크나이저·선택적 LoRA를 준비하고, `local_model.py`에서 토큰 한도와 GPU 실행을 관리한다.
- 요청 취소 후 실제 GPU 실행이 끝날 때까지 실행 잠금을 유지한다. 재생성·복구와 DB 확정은 기존 수사 흐름을 따르며 fixture는 기존 테스트 대역을 사용한다.

## 검증

- `pyproject.toml`의 Ruff 설정, 파일당 250줄 기준과 기존 docstring 형식을 따른다. `python -m ruff check app scripts tests`, `python -m ruff format --check app scripts tests`, `python -m pytest -q`를 실행한다.
- 구조 변경 시 공개 HTTP 계약, 수사 재개, 중복 요청·revision 충돌, 심문 실패 후 예약 해제를 확인한다.
- 모델 실행 경로를 변경할 때는 같은 Qwen 사례에서 대사 생성, 검증 호출, 모델 버전과 토큰 한도 오류를 확인한다. 시간 초과와 잘못된 출력에서는 그래프 복구와 DB 확정 여부를 확인한다. fixture와 실제 Qwen에서 확인한 범위 및 미검증 항목을 기록한다.

## Python docstring

- 선언 바로 아래에 삼중 큰따옴표로 작성한다. 요약 뒤에 빈 줄을 두고 `Args:`, `Returns:` 순서로 적는다. 인자는 `이름: 설명`, 반환값은 `타입: 설명` 형식을 사용한다.
- `self`와 `cls`는 생략한다. 인자가 없으면 `Args:`에 `없음.`을, 반환값이 없으면 `Returns:`에 `None: 반환값 없음.`을 적는다. 비동기 함수는 await한 결과를 설명한다.
- 클래스 docstring에는 생성자 인자와 인스턴스의 역할을 적고, `__init__`에는 메서드 형식을 적용한다. 호출자가 처리해야 하는 예외는 `Returns:` 뒤의 `Raises:`에 발생 조건과 함께 적는다.
