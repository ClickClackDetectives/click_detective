# Click Detective — Next.js

## 개요

Click Detective(딸깍탐정단)는 증거 조사, 용의자 심문, 자료 조합과 고발을 통해 사건을 해결하는 웹 기반 탐정 게임입니다. 이 프로젝트는 플레이어 화면과 FastAPI 연결을 담당하는 Next.js 프런트엔드입니다.

`click_detective_FastAPI`가 사건 데이터, 게임 규칙, 저장 및 AI 대사를 처리하고, Next.js는 화면과 서버 중계 계층(BFF)을 제공합니다.

## 프로젝트 소개

- 홈, 사건 기록실, 준비 중 사건 안내 및 오프닝
- 증거 보관실과 자료 열람·검색
- 용의자 심문, 증언 확인 및 자료 조합 추론
- 수사 진행률, 고발 제출 및 결과 표시
- 수사 이어하기와 메모 자동 저장
- 반응형 화면, 팝업 및 게임 토큰의 HttpOnly 쿠키 관리

브라우저 요청은 Next.js 서버를 거쳐 FastAPI로 전달됩니다. 사건 정답·추론 규칙·모델 파일은 백엔드에서 관리하고, 서버 간 API 키는 Next.js 서버에서 사용합니다.

## 기술 스택

| 구분 | 기술 |
| --- | --- |
| 프레임워크 | Next.js 16.4.6, App Router |
| UI | React 19.3.1, React DOM |
| 언어 | TypeScript 5 |
| 스타일 | CSS, 반응형 스타일시트 |
| 아이콘 | Lucide React |
| 서버 연동 | Route Handlers, Fetch API, server-only |
| 테스트 | Node.js 내장 테스트 러너, Playwright |
| 포맷 | Prettier |
| 실행 환경 | Node.js 22.18.0 이상, npm |

버전과 실행 스크립트는 `package.json`에 정의되어 있습니다.

## 설치 및 실행 방법

두 프로젝트가 같은 상위 폴더에 있는 Bash 환경을 기준으로 합니다.

```text
상위 폴더/
├── click_detective_FastAPI/
└── click_detective_Next_js/
```

### 1. 백엔드 실행

먼저 백엔드 README에 따라 가상환경, 의존성과 `.env`를 준비합니다. 터미널 A에서 GPU 없이 실행하려면 다음 명령을 사용합니다.

```bash
cd click_detective_FastAPI
source .cd_venv/bin/activate
CLICK_GENERATION_MODE=fixture python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

http://127.0.0.1:8000/healthz 에서 `{"status":"ok"}` 응답을 확인합니다. 실제 AI 대사는 모델·어댑터·GPU 환경을 준비하고 `local` 모드로 실행해야 합니다.

### 2. 프런트엔드 설치

Node.js 22.18.0 이상과 npm을 준비한 뒤, 별도 터미널 B에서 실행합니다.

```bash
cd click_detective_Next_js
npm ci
```

### 3. 환경변수 설정

처음 설치하는 경우 예제 파일을 복사합니다. 기존 `.env.local`이 있다면 직접 수정합니다.

```bash
cp -n .env.local.example .env.local
```

```dotenv
CLICK_DETECTIVE_API_URL=http://127.0.0.1:8000
CLICK_DETECTIVE_API_KEY=백엔드_CLICK_API_KEY와_같은_값
CLICK_DETECTIVE_TIMEOUT_MS=120000
```

| 변수 | 설명 |
| --- | --- |
| `CLICK_DETECTIVE_API_URL` | Next.js 서버에서 접근할 FastAPI 주소 |
| `CLICK_DETECTIVE_API_KEY` | 백엔드 `CLICK_API_KEY`와 동일한 서비스 키 |
| `CLICK_DETECTIVE_TIMEOUT_MS` | 백엔드 요청 제한 시간(밀리초) |

Next.js는 백엔드 `.env`를 자동으로 읽지 않습니다. API 키를 직접 맞추고 `NEXT_PUBLIC_` 변수에 넣지 않습니다. 두 서버가 다른 컴퓨터·컨테이너에 있다면 Next.js에서 접근 가능한 백엔드 주소를 지정합니다. 환경변수 변경 후 Next.js를 재시작합니다.

### 4. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 http://localhost:3000 에 접속합니다. 사건 조회와 게임 진행에는 백엔드도 실행 중이어야 합니다.

다른 포트를 사용하려면 다음과 같이 실행합니다.

```bash
npm run dev -- --port 3001
```

### 5. 배포용 빌드 및 실행

개발 서버를 종료한 뒤 실행합니다.

```bash
npm run build
npm run start
```

기본 접속 주소는 http://localhost:3000 입니다. 코드 변경 후에는 다시 빌드합니다.

## 검사 및 테스트

```bash
npm run typecheck
npm test
npm run build
```

통합 검사는 빌드 결과와 백엔드 `.cd_venv/bin/python`을 사용합니다. 스크립트의 기본 백엔드 폴더명이 현재와 다르므로 경로를 명시합니다.

```bash
CLICK_TEST_BACKEND_DIR=../click_detective_FastAPI npm run test:integration
```

UI 검사에는 Playwright Chromium이 필요합니다.

```bash
npx playwright install chromium
CLICK_TEST_BACKEND_DIR=../click_detective_FastAPI npm run test:ui
```

통합 검사는 별도의 fixture 백엔드와 Next.js를 실행하며 결과를 `.reports/integration.json`에 저장합니다. 실제 LLM 대사 품질 검사는 포함하지 않습니다.

## 추가 문서

- 전체 문서: `docs/README.md`
- 실행·설정 상세: `docs/01_설치와_실행.md`
- 구조와 데이터 흐름: `docs/02_구조와_데이터흐름.md`
- 화면 사용법: `docs/03_화면_사용법.md`
- API 연결표: `docs/04_API_연결표.md`
- UI·UX 검사: `docs/09_원본_UI_UX_유지와_비교검사.md`

기존 상세 문서의 `click_detective`, `click_detective_nextjs`는 각각 현재 `click_detective_FastAPI`, `click_detective_Next_js`에 해당합니다.
