# 화면에서 FastAPI까지 코드 찾기

페이지에서 시작해 기능 컴포넌트, `app/game/`의 화면 상태, 브라우저 요청, Route Handler 순으로 호출을 추적할 수 있습니다. 각 문서는 함수 선언과 역할, 입력, 반환값 및 소스 위치를 제공합니다.

## 게임 화면

| 기능 | 구현 폴더 |
| --- | --- |
| [앱 조립과 공통 레이아웃](화면/공통화면.md) | `components/application/` |
| [홈부터 사건 오프닝까지](화면/사건시작.md) | `components/catalog/` |
| [증거 열람과 상세 문서](화면/증거.md) | `components/materials/` |
| [증언 및 심문 기록](화면/증언.md) | `components/testimony/` |
| [심문 입력과 대화](화면/심문.md) | `components/interrogation/` |
| [발견한 쟁점 목록](화면/쟁점.md) | `components/findings/` |
| [추론 자료 선택과 결과](화면/추론.md) | `components/inference/` |
| [사건 타임라인](화면/타임라인.md) | `components/timeline/` |
| [수사 메모](화면/메모.md) | `components/notes/` |
| [고발 제출과 판정 표시](화면/고발과결과.md) | `components/accusation/` |

## 화면 상태와 요청

| 기능 | 구현 폴더 |
| --- | --- |
| [공개 사건 데이터](게임로직/공개자료.md) | `app/game/catalog/` |
| [수사 생성·재개·행동](게임로직/수사상태와요청.md) | `app/game/investigation/` |
| [화면용 자료 조회](게임로직/자료조회.md) | `app/game/materials/` |
| [증언 그룹과 분류](게임로직/진술분류.md) | `app/game/testimony/` |
| [인물별 공개 질문](게임로직/질문주제.md) | `app/game/interrogation/` |
| [추론 자료 식별자](게임로직/추론출처.md) | `app/game/inference/` |
| [메모 자동 저장](게임로직/메모자동저장.md) | `app/game/notes/` |
| [고발 화면 준비 상태](게임로직/고발준비.md) | `app/game/accusation/` |

## 서버 통신

| 기능 | 구현 폴더 |
| --- | --- |
| [페이지와 Route Handler 진입점](서버/진입점.md) | `app/` |
| [인증과 FastAPI 중계](서버/API중계.md) | `server/proxy/` |
| [브라우저 JSON 요청과 오류](서버/브라우저요청.md) | `shared/api/` |

## 검사 실행 코드

| 기능 | 구현 폴더 |
| --- | --- |
| [두 서버의 HTTP 통합 검사](검사/통합검사.md) | `scripts/integration/` |
| [브라우저 조작과 화면 검사](검사/화면검사.md) | `scripts/ui/` |
| [검사 진입점과 보고서](검사/실행스크립트.md) | `scripts/` |

[Next.js 문서 목차](../README.md)
