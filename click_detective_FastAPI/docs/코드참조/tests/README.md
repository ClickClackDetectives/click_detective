# FastAPI 회귀 검사 코드

공통 fixture에서 테스트용 앱과 DB를 준비합니다. 사건 공개 응답, 심문 그래프, 수사 상태 변경은 담당 도메인의 테스트에서 확인합니다.

[공통 fixture](conftest.md) · [사건 카탈로그](cases/test_catalog.md) · [대화 실행](dialogue/test_runner.md) · [수사 HTTP 계약](investigation/test_api_routes.md)

| 소스 폴더 | 파일별 참조 |
| --- | --- |
| `tests/` | [`__init__.py`](__init__.md) · [`conftest.py`](conftest.md) · [`test_code_conventions.py`](test_code_conventions.md) |
| `tests/cases/` | [`__init__.py`](cases/__init__.md) · [`test_catalog.py`](cases/test_catalog.md) |
| `tests/dialogue/` | [`__init__.py`](dialogue/__init__.md) · [`models.py`](dialogue/models.md) · [`test_free_question_recovery.py`](dialogue/test_free_question_recovery.md) · [`test_reply_availability.py`](dialogue/test_reply_availability.md) · [`test_runner.py`](dialogue/test_runner.md) · [`test_runtime.py`](dialogue/test_runtime.md) · [`test_trace_and_timeout.py`](dialogue/test_trace_and_timeout.md) |
| `tests/dialogue/inference_agent/` | [`test_paraphrase_generation.py`](dialogue/inference_agent/test_paraphrase_generation.md) |
| `tests/investigation/` | [`__init__.py`](investigation/__init__.md) · [`data_helpers.py`](investigation/data_helpers.md) · [`player.py`](investigation/player.md) · [`test_api_routes.py`](investigation/test_api_routes.md) · [`test_game_progress.py`](investigation/test_game_progress.md) · [`test_invalid_actions.py`](investigation/test_invalid_actions.md) · [`test_minimum_success_route.py`](investigation/test_minimum_success_route.md) · [`test_open_accusation.py`](investigation/test_open_accusation.md) · [`test_screen_views.py`](investigation/test_screen_views.md) |

[FastAPI 코드 참조](../README.md)
