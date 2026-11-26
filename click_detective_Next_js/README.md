# Click Detective — Next.js

탐정 게임의 화면과 FastAPI 서버 연결을 담당합니다. 화면은 `components/`, 화면에서 사용하는 게임 로직은 `app/game/`, CSS는 `styles/`, 서버 중계는 `server/proxy/`에 있습니다. 사건 규칙·저장·AI 에이전트는 [FastAPI](../click_detective_FastAPI/README.md)가 처리합니다.

## 빠른 실행

Node.js 22.18.0 이상이 필요합니다. 먼저 [FastAPI 실행 안내](../click_detective_FastAPI/README.md)에 따라 백엔드를 실행하세요. GPU 없이 연결을 확인할 때는 백엔드의 `CLICK_GENERATION_MODE=fixture`를 사용합니다.

```bash
cd click_detective_Next_js
npm ci
cp .env.local.example .env.local
```

기존 `.env.local`이 있다면 복사하지 말고 값을 확인합니다.

```dotenv
CLICK_DETECTIVE_API_URL=http://127.0.0.1:8000
CLICK_DETECTIVE_API_KEY=백엔드_CLICK_API_KEY와_같은_값
CLICK_DETECTIVE_TIMEOUT_MS=120000
```

키는 백엔드 `.env`와 일치해야 하며 Next.js 서버에서만 사용합니다. 설정을 바꿨다면 Next.js를 재시작합니다.

```bash
npm run dev
```

`http://localhost:3000`에 접속합니다. 배포용 실행은 `npm run build` 후 `npm run start`입니다.

## 대시보드

- `/agent-dashboard`에서 에이전트 실행 기록을 확인합니다.
- `/rag-dashboard`에서 E5·ChromaDB와 Kiwi BM25 결합의 오프라인 평가를 비교합니다. 평가 세트와 유사도·가중치 설정을 선택하면 저장된 측정 결과가 바뀝니다. [평가 방법과 결과](../click_detective_FastAPI/docs/변경이력/자유_심문_RAG_변경_정리.md)

## 구조

```text
app/                    Next.js 진입점·주소
app/game/               게임 상태·요청·훅·타입
components/             기능별 화면·팝업 컴포넌트
styles/                 전역·화면별·반응형 CSS
shared/api/           브라우저 공통 요청
server/proxy/         경로·인증·입력·응답 중계
hooks/ lib/             이전 import 경로와 호환하는 재내보내기
scripts/              통합 검사·화면 비교
tests/               단위·코드 규칙 검사
docs/                실행·동작 순서·함수 설명
```

각 소스는 주석 포함 250줄 이내이며 이름 있는 함수·클래스에 역할·파라미터·반환값 JSDoc을 작성합니다. 화면의 React 컴포넌트와 훅, 일반 함수로 구성되어 있습니다.

## 검사

```bash
npm test
npm run typecheck
npm run build
npm run test:integration
```

통합 검사는 형제 `click_detective_FastAPI`의 가상환경을 찾아 임시 fixture 서버와 DB를 사용합니다. 브라우저 비교는 Chromium과 이전 UI 소스가 추가로 필요합니다.

```bash
npx playwright install chromium
CLICK_TEST_ORIGINAL_DIR=/이전/UI/프로젝트 npm run test:ui
```

포트·Python 경로·결과 보고서는 [검사 안내](docs/테스트/검사와_오류해결.md)를 참고하세요. fixture 검사는 실제 GPU·LLM 응답 품질 검사를 포함하지 않습니다.

## 문서

- [전체 안내](docs/README.md)
- [초보자 안내](docs/시작하기/초보자_안내.md)
- [설치와 실행](docs/시작하기/설치와_실행.md)
- [폴더 구조](docs/구조/폴더_구조.md) · [실행 순서](docs/구조/동작_순서.md)
- [화면 사용법](docs/화면/화면_사용법.md)
- [API 연결표](docs/서버연결/API_연결표.md) · [인증과 상태](docs/서버연결/인증과_상태관리.md)
- [실제 함수·클래스 선언과 설명](docs/코드참조/README.md)
- [리팩토링 내용](docs/변경이력/리팩토링.md) · [검증 기록](docs/테스트/검증_기록.md)
- [CSS 구조](docs/구조/CSS_구조와_적용순서.md) · [코드 발표 순서](docs/발표/코드로_설명하는_동작순서.md)
