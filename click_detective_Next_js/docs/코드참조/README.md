# 함수·클래스 코드 설명서

현재 구현의 실제 선언을 코드 블록으로 보여주고 역할·입력·반환값을 설명합니다. 본문 전체는 각 파일의 소스 링크에서 확인합니다. 화면 선언의 `Props`는 바로 위에 정의된 입력 타입입니다.

| 구분 | 설명 |
| --- | --- |
| [앱 조립과 공통 화면](application.md) | `features/application` |
| [사건 자료와 시작 화면](catalog.md) | `features/catalog` |
| [수사 상태와 행동 요청](investigation.md) | `features/investigation` |
| [증거와 자료 조회](materials.md) | `features/materials` |
| [증언 기록](testimony.md) | `features/testimony` |
| [용의자 심문](interrogation.md) | `features/interrogation` |
| [발견한 쟁점](findings.md) | `features/findings` |
| [자료 연결과 추론](inference.md) | `features/inference` |
| [사건 타임라인](timeline.md) | `features/timeline` |
| [메모와 자동 저장](notes.md) | `features/notes` |
| [고발과 결과](accusation.md) | `features/accusation` |
| [FastAPI 서버 중계](서버중계.md) | `server/proxy` |
| [브라우저 공통 요청](공통요청.md) | `shared/api` |
| [Next.js 주소와 진입점](진입점.md) | `app` |
| [전체 게임 연결 검사](통합검사.md) | `scripts/integration` |
| [브라우저 화면 검사](화면검사.md) | `scripts/ui` |
| [검사 시작 함수](검사실행.md) | `scripts` |

처음에는 [수사 상태와 요청](investigation.md)의 `useCaseGame`, `requestGame`, `mapGameCommand`를 읽고 [서버 중계](서버중계.md)의 `handle`로 이어가세요. 작은 타입·상수 파일도 각 목록에 포함되어 있습니다. 호환용 `components`, `hooks`, `lib`는 기능 구현을 다시 내보내므로 새 경로의 설명서를 사용합니다.

[초보자 안내](../시작하기/초보자_안내.md) · [동작 순서](../구조/동작_순서.md) · [문서 첫 화면](../README.md)
