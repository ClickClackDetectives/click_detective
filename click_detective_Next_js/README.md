# Click Detective Next.js

사건을 선택하고 증거를 조사하며 용의자를 심문하는 브라우저 화면입니다. Next.js는 입력과 화면 상태를 관리하고, 서버에서 FastAPI에 요청을 전달합니다. 사건 규칙과 수사 결과는 [FastAPI](../click_detective_FastAPI/README.md)에서 처리합니다.

## 로컬 실행

Node.js 22.18.0 이상을 준비하고 FastAPI를 먼저 실행합니다. 모델 없이 화면을 확인할 때는 FastAPI의 fixture 모드를 사용합니다.

저장소 루트에서 실행합니다.

```bash
cd click_detective_Next_js
npm ci
cp -n .env.local.example .env.local
```

`.env.local`을 열고 서비스 키를 실제 값으로 교체합니다.

```dotenv
CLICK_DETECTIVE_API_URL=http://127.0.0.1:8000
CLICK_DETECTIVE_API_KEY=replace-with-the-same-key-as-CLICK_API_KEY
CLICK_DETECTIVE_TIMEOUT_MS=120000
```

API URL은 Next.js 서버에서 접근할 수 있어야 합니다. 서비스 키는 FastAPI의 `CLICK_API_KEY`와 일치해야 하며 서버 환경변수로 관리합니다.

```bash
npm run dev
```

`http://localhost:3000`에서 사건을 선택하고 수사를 시작합니다. 운영 빌드는 `npm run build` 후 `npm run start`로 실행합니다. [설치와 실행 상세](docs/시작하기/설치와_실행.md)

## 프로젝트 구조

```text
click_detective_Next_js/
├── app/
│   ├── layout.tsx               # 공통 레이아웃
│   ├── page.tsx                 # 홈 진입점
│   ├── login/                   # 로그인 페이지
│   ├── signup/                  # 가입 페이지
│   ├── agent-dashboard/         # 에이전트 진단 페이지
│   ├── rag-dashboard/           # 검색 평가 페이지
│   ├── assets/                  # 자산 요청 처리
│   ├── api/
│   │   ├── auth/[operation]/route.ts        # 계정 Route Handler
│   │   └── detective/[...segments]/route.ts # 게임 Route Handler
│   └── game/
│       ├── page.tsx             # 게임 페이지
│       ├── catalog/             # 공개 사건 자료
│       ├── investigation/       # 수사 상태, 행동 요청, 재개
│       ├── materials/           # 자료 조회와 화면 데이터
│       ├── interrogation/       # 공개 질문 주제
│       ├── testimony/           # 증언 그룹과 분류
│       ├── inference/           # 추론 출처 표시와 식별자
│       ├── notes/               # 메모 자동 저장
│       └── accusation/          # 고발 준비 상태
├── components/
│   ├── application/             # 게임 화면 조립
│   ├── auth/                    # 계정 관련 화면
│   ├── catalog/                 # 사건 선택, 브리핑, 오프닝
│   ├── materials/               # 증거 목록과 상세 팝업
│   ├── interrogation/           # 심문 입력과 대화
│   ├── testimony/               # 증언과 심문 기록
│   ├── findings/                # 쟁점
│   ├── inference/               # 추론 자료 선택과 결과
│   ├── timeline/                # 타임라인
│   ├── notes/                   # 메모 입력
│   └── accusation/              # 고발 입력과 수사 결과
├── server/
│   ├── auth/                    # 계정 요청 중계와 세션 쿠키
│   ├── diagnostics/             # 진단 기록 조회
│   └── proxy/
│       ├── handle.ts            # 게임 중계 진입점
│       ├── policy.ts            # 중계 경로와 메서드 규칙
│       ├── request.ts           # 쿼리와 본문 처리
│       ├── upstream.ts          # FastAPI 호출
│       └── responses.ts         # 브라우저 응답과 오류 처리
├── shared/
│   └── api/                     # 브라우저 공통 요청과 오류
├── styles/                      # 공통·화면별·반응형 CSS
├── hooks/                       # 기존 훅 import 경로
├── lib/                         # 기존 유틸리티 import 경로
├── scripts/                     # 통합 검사와 브라우저 검사
├── tests/                       # 회귀 테스트와 코드 규칙
├── docs/                        # 실행·화면·코드 안내
└── package.json                 # 의존성과 npm 명령
```

`/agent-dashboard`에서는 대화 에이전트의 실행을 확인하고, `/rag-dashboard`에서는 저장된 자유 질문 검색 평가를 비교합니다. [에이전트 대시보드 설정](docs/테스트/에이전트_대시보드.md) · [검색 평가 기록](../click_detective_FastAPI/docs/변경이력/자유_심문_RAG_변경_정리.md) · [코드 참조](docs/코드참조/README.md)

## 사용 기술

| 기술 | 용도 |
| --- | --- |
| Node.js 22.18.0+, npm | Next.js 실행과 의존성 관리 |
| Next.js App Router, Route Handlers | 페이지 라우팅과 FastAPI 요청 중계 |
| React, TypeScript | 화면 컴포넌트, 상태와 훅, API 데이터 타입 |
| CSS | 공통·화면별 스타일과 반응형 레이아웃 |
| Lucide React, Recharts | 화면 아이콘과 대시보드 차트 |
| Prettier, Node.js 테스트 러너, Playwright | 포맷 확인, 회귀 테스트, 브라우저 검사 |

[프런트엔드 의존성 및 실행 명령](package.json)

## 개발 확인

```bash
npm run format:check
npm run typecheck
npm test
```

두 서버의 연결을 검사하려면 `npm run build` 후 `npm run test:integration`을 실행합니다. Python 환경과 DB fixture, Chromium을 사용하는 화면 검사의 준비 사항은 [검사 안내](docs/테스트/검사와_오류해결.md)에 있습니다. 화면과 코드 설명은 [문서 목차](docs/README.md)에서 찾을 수 있습니다.
