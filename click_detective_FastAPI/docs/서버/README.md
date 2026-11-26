# DB 연결과 서버 운영

MongoDB replica set은 수사의 진행 상태를 저장합니다. 계정 기능을 활성화하면 PostgreSQL에서 계정과 세션을 관리하고, Next.js 서버가 인증 정보를 전달합니다.

## 읽을 문서

- replica set 초기화와 연결 문자열을 확인합니다. [MongoDB 설정](MongoDB_설치와_실행.md)
- 계정용 DB와 역할을 만들고 접속을 확인합니다. [PostgreSQL 설정](PostgreSQL_설치와_실행.md)
- 수사 토큰, 상태 버전, 요청 예약과 확정의 저장 흐름을 읽습니다. [수사 저장](수사_저장.md)
- FastAPI 주소와 서비스 키 설정을 맞춥니다. [Next.js 연결](Nextjs_연결.md)
- 초기화 또는 요청 중 어느 단계에서 문제가 발생했는지 찾습니다. [전체 처리 흐름](../시작하기/03_전체_처리_흐름.md)

[상위 목차](../README.md)
