# 계정 요청과 PostgreSQL 코드

가입·로그인 요청은 컨트롤러를 거쳐 계정 서비스로 전달됩니다. 세션과 토큰 교체는 저장소에서 처리하며, 탈퇴의 수사 데이터 정리는 탈퇴 서비스에서 이어집니다.

[HTTP 시작점](controllers/auth_controller.md) · [계정 처리](services/auth_service.md) · [탈퇴 처리](services/auth_deletion_service.md)

| 소스 폴더 | 파일별 참조 |
| --- | --- |
| `app/auth/controllers/` | [`auth_controller.py`](controllers/auth_controller.md) · [`auth_request_context.py`](controllers/auth_request_context.md) |
| `app/auth/dto/` | [`auth_contracts.py`](dto/auth_contracts.md) |
| `app/auth/providers/` | [`auth_provider.py`](providers/auth_provider.md) |
| `app/auth/repositories/` | [`auth_deletion_repository.py`](repositories/auth_deletion_repository.md) · [`auth_rate_limit_repository.py`](repositories/auth_rate_limit_repository.md) · [`auth_repository.py`](repositories/auth_repository.md) · [`auth_schema.py`](repositories/auth_schema.md) · [`auth_token_rotation.py`](repositories/auth_token_rotation.md) |
| `app/auth/services/` | [`auth_deletion_service.py`](services/auth_deletion_service.md) · [`auth_errors.py`](services/auth_errors.md) · [`auth_service.py`](services/auth_service.md) · [`auth_tokens.py`](services/auth_tokens.md) |

[FastAPI 코드 참조](../../README.md)
