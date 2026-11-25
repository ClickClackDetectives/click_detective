# 서버와 수사 저장

[전체 목차](../README.md)

| 문서 | 내용 |
|---|---|
| [PostgreSQL 설치와 실행](PostgreSQL_설치와_실행.md) | Ubuntu 설치, 앱 역할·DB 생성, 서비스 및 로컬 소켓 확인 |
| [MongoDB 설치와 실행](MongoDB_설치와_실행.md) | Ubuntu 설치, replica set·인증 설정, 서비스 및 로컬 프로세스 확인 |
| [수사 저장](수사_저장.md) | 사건 데이터·내부 상태·수사 토큰·예약·확정·충돌 |
| [Next.js 연결](Nextjs_연결.md) | 화면 서버와 FastAPI의 책임 구분 |
| [전체 처리 흐름](../시작하기/03_전체_처리_흐름.md) | 시작·조회·변경 요청의 호출 순서 |

읽기 시작할 소스는 [GameService](../../app/investigation/service.py), [MongoRepository](../../app/investigation/persistence/mongo_repository.py), [Catalog](../../app/cases/catalog.py)다.
