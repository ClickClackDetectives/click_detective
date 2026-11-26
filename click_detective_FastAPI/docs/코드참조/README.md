# 실행 경로별 FastAPI 코드 참조

`app.main:app`이 라우터를 등록하고 lifespan이 운영 의존성을 준비합니다. 아래 색인에서 담당 도메인을 고르면 파일별 선언과 실제 구현 링크로 이어집니다. [앱 진입점](app/main.md) · [런타임](app/runtime/README.md)

| 찾는 기능 | 코드 참조 |
| --- | --- |
| 가입, 로그인, 세션 갱신, 탈퇴 | [계정](app/auth/README.md) |
| 사건 파일, 공개 카탈로그, 자산 | [사건](app/cases/README.md) |
| 상태 변경, 자료 획득, 판정, MongoDB | [수사](app/investigation/README.md) |
| 진술 검색, 프롬프트, 생성과 검증 | [대화](app/dialogue/README.md) |
| 실서버 호출 및 배치 실행 | [스크립트](scripts/README.md) |

## 회귀 테스트

테스트에 사용하는 데이터와 코드 위치는 [테스트 색인](tests/README.md), 명령과 환경 설정은 [검사 안내](../테스트/README.md)에서 확인합니다.
