# FastAPI 코드 참조

[FastAPI 문서 홈](../README.md) · [코드 읽는 순서](../시작하기/04_코드_읽는_순서.md)

파일별 문서 경로는 Python 소스 경로를 따른다. 각 문서에서 선언 위치와 전체 구현으로 이동할 수 있다.

## 앱 시작

- [FastAPI 진입점](app/main.md)
- [공통 런타임](app/runtime/README.md)

## 업무 도메인

- [`auth` · 계정 인증](app/auth/README.md)
- [`cases` · 사건 카탈로그](app/cases/README.md)
- [`dialogue` · 대화 생성과 검증](app/dialogue/README.md)
- [`investigation` · 수사와 저장](app/investigation/README.md)

## 운영 스크립트

[배치·실서버 검사 코드](scripts/README.md)

## 회귀 테스트

[테스트와 fixture 코드](tests/README.md)
