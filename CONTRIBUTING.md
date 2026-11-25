# Click Detective 기여 가이드

변경 전에 [공통 규칙](AGENTS.md)과 담당 프로젝트의 규칙을 확인한다. [FastAPI](click_detective_FastAPI/AGENTS.md) · [Next.js](click_detective_Next_js/AGENTS.md)

## 변경 예시

| 수정할 내용 | 코드 위치와 확인할 동작 |
| --- | --- |
| 증언 화면 문구 | `components/testimony/`에서 해당 문구를 찾아 수정한다. 진술 목록과 빈 상태에서 문구가 자연스러운지 확인한다. |
| 증언 검색·분류 | `useScreenView`에 전달하는 조회 조건과 화면 필터를 확인한다. 인물과 분류를 함께 선택했을 때 기대한 기록이 나온다는 것을 확인한다. |
| 진술 획득 조건 | FastAPI의 `app/investigation/rules/`에서 조건을 수정한다. 조건 충족 전후에 서버 응답과 화면 표시가 각각 맞는지 확인한다. |
| API 응답 필드 | FastAPI 스키마와 Next.js 타입·호출부를 함께 확인한다. 저장된 수사를 재개할 때도 응답을 읽을 수 있는지 확인한다. |
| 메모 저장 또는 심문 | 기존 요청 식별자와 상태 버전을 사용한다. 동일 요청 재시도와 오래된 버전으로 보낸 요청의 응답을 확인한다. |

## 로컬 검증

FastAPI 디렉터리에서 개발 의존성이 설치된 Python으로 실행한다. 수사 fixture에는 `CLICK_TEST_MONGO_URI`를 설정하고, 계정 검사에는 `CLICK_TEST_POSTGRES_DSN`도 설정한다.

```sh
python -m ruff check app scripts tests
python -m ruff format --check app scripts tests
python -m pytest -q
```

Next.js 디렉터리에서 `npm ci` 후 실행한다.

```sh
npm run format:check
npm run typecheck
npm test
```

API 계약이나 수사 흐름이 양쪽에 걸쳐 바뀌면 Next.js 디렉터리에서 빌드 후 통합 검사를 실행한다. FastAPI 개발 의존성을 설치한 Python이 기본 탐색 경로에 없으면 `CLICK_TEST_PYTHON`에 실행 파일 경로를 지정한다.

```sh
npm run build
npm run test:integration
```

통합 검사는 fixture 모드와 임시 MongoDB DB와 PostgreSQL 스키마를 사용한다. 실제 모델 응답 품질은 [실서버 LLM 검사 안내](click_detective_FastAPI/docs/테스트/실서버_LLM_검사.md)를 따른다.
