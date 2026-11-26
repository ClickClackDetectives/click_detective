# 실서버 심문 검사 코드

단일 실서버 검사와 130개 예제 배치의 진입점을 찾을 수 있습니다. 호출·응답 확인·진단 기록 조립은 live_dialogue 모듈에서 처리합니다.

[실서버 검사 진입점](test_llm_api_live.md) · [예제 배치 진입점](run_130_live_examples.md)

| 소스 폴더 | 파일별 참조 |
| --- | --- |
| `scripts/` | [`__init__.py`](__init__.md) · [`run_130_live_examples.py`](run_130_live_examples.md) · [`test_llm_api_live.py`](test_llm_api_live.md) |
| `scripts/live_dialogue/` | [`__init__.py`](live_dialogue/__init__.md) · [`case_runner.py`](live_dialogue/case_runner.md) · [`definitions.py`](live_dialogue/definitions.md) · [`errors.py`](live_dialogue/errors.md) · [`example_reports.py`](live_dialogue/example_reports.md) · [`examples.py`](live_dialogue/examples.md) · [`tester.py`](live_dialogue/tester.md) · [`traces.py`](live_dialogue/traces.md) · [`transport.py`](live_dialogue/transport.md) |

[FastAPI 코드 참조](../README.md)
