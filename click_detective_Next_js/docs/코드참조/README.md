# 현재 코드의 함수·클래스 설명서

화면과 로직을 구분해 현재 파일의 선언·역할·입력·반환값을 설명합니다. 본문 전체 대신 함수 선언을 코드 블록으로 보여주며, 실제 구현은 각 소스 링크에서 확인합니다.

처음 읽는다면 [수사 상태와 요청](게임로직/수사상태와요청.md) → [브라우저 공통 요청](서버/브라우저요청.md) → [서버 중계](서버/API중계.md) 순서로 따라가세요. 화면의 조립은 [공통 화면](화면/공통화면.md)에 있습니다.

## 화면

| 문서 | 소스 위치 |
| --- | --- |
| [앱 조립과 공통 화면](화면/공통화면.md) | `components/application/` |
| [홈·사건 선택·브리핑·오프닝](화면/사건시작.md) | `components/catalog/` |
| [증거 목록과 문서 팝업](화면/증거.md) | `components/materials/` |
| [증언과 심문 기록](화면/증언.md) | `components/testimony/` |
| [용의자 심문 화면](화면/심문.md) | `components/interrogation/` |
| [발견한 쟁점 화면](화면/쟁점.md) | `components/findings/` |
| [자료 선택과 확보 추론 화면](화면/추론.md) | `components/inference/` |
| [사건 타임라인 화면](화면/타임라인.md) | `components/timeline/` |
| [메모 입력 화면](화면/메모.md) | `components/notes/` |
| [고발 입력과 수사 결과 화면](화면/고발과결과.md) | `components/accusation/` |

## 게임로직

| 문서 | 소스 위치 |
| --- | --- |
| [공개 사건 자료와 타입](게임로직/공개자료.md) | `app/game/catalog/` |
| [수사 상태·행동 요청·복원](게임로직/수사상태와요청.md) | `app/game/investigation/` |
| [문서 타입과 화면 조회](게임로직/자료조회.md) | `app/game/materials/` |
| [증언 화면의 분류](게임로직/진술분류.md) | `app/game/testimony/` |
| [공개 질문 주제](게임로직/질문주제.md) | `app/game/interrogation/` |
| [추론 출처의 표시와 식별자](게임로직/추론출처.md) | `app/game/inference/` |
| [메모 자동 저장](게임로직/메모자동저장.md) | `app/game/notes/` |
| [고발 준비도 표시](게임로직/고발준비.md) | `app/game/accusation/` |

## 서버

| 문서 | 소스 위치 |
| --- | --- |
| [Next.js 페이지와 Route Handler](서버/진입점.md) | `app/` |
| [Next.js 서버의 FastAPI 중계](서버/API중계.md) | `server/proxy/` |
| [브라우저 공통 요청과 오류](서버/브라우저요청.md) | `shared/api/` |

## 검사

| 문서 | 소스 위치 |
| --- | --- |
| [실제 HTTP 통합 검사](검사/통합검사.md) | `scripts/integration/` |
| [브라우저 화면과 조작 검사](검사/화면검사.md) | `scripts/ui/` |
| [검사 실행과 보고서](검사/실행스크립트.md) | `scripts/` |

`components/기능명/`은 실제 화면 구현입니다. `components` 바로 아래의 예전 단일 파일·`components/screens/`·`hooks/`·`lib/`는 호환 경로이므로 실제 구현의 설명서를 사용합니다.

[초보자 안내](../시작하기/초보자_안내.md) · [문서 첫 화면](../README.md)
