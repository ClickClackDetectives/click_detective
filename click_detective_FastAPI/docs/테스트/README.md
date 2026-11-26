# FastAPI 검사 실행과 결과 확인

FastAPI 디렉터리에서 개발 의존성이 설치된 가상환경을 활성화한 뒤 실행합니다.

```bash
python -m ruff check app scripts tests
python -m ruff format --check app scripts tests
python -m pytest -q
```

수사 fixture에는 `CLICK_TEST_MONGO_URI`를, 계정 검사에는 `CLICK_TEST_POSTGRES_DSN`도 설정합니다. pytest 요약에서 건너뛴 테스트를 확인하면 DB 연결이 필요한 범위를 파악할 수 있습니다.

| 확인할 작업 | 문서 |
| --- | --- |
| 검사 실패 원인과 진단 이벤트 찾기 | [자동 검사와 문제 해결](자동검사와_문제해결.md) |
| local 서버에 요청해 Qwen 응답과 검증 결과 확인 | [실서버 LLM 검사](실서버_LLM_검사.md) |
| 이전 검사 결과와 실행 범위 확인 | [최근 검사 결과](최근_검사_결과.md) |
| fixture와 도메인별 테스트 코드 찾기 | [테스트 코드 참조](../코드참조/tests/README.md) |
