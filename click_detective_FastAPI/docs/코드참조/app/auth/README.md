# 계정 인증

[코드 참조 홈](../../README.md)

계정·세션과 탈퇴 작업을 처리하고 PostgreSQL에 저장한다.

## HTTP 컨트롤러

- [`controllers/auth_controller.py`](controllers/auth_controller.md)
- [`controllers/auth_request_context.py`](controllers/auth_request_context.md)

## 서비스와 규칙

- [`services/auth_deletion_service.py`](services/auth_deletion_service.md)
- [`services/auth_errors.py`](services/auth_errors.md)
- [`services/auth_service.py`](services/auth_service.md)
- [`services/auth_tokens.py`](services/auth_tokens.md)

## 데이터 계약

- [`dto/auth_contracts.py`](dto/auth_contracts.md)

## 저장소

- [`repositories/auth_deletion_repository.py`](repositories/auth_deletion_repository.md)
- [`repositories/auth_rate_limit_repository.py`](repositories/auth_rate_limit_repository.md)
- [`repositories/auth_repository.py`](repositories/auth_repository.md)
- [`repositories/auth_schema.py`](repositories/auth_schema.md)
- [`repositories/auth_token_rotation.py`](repositories/auth_token_rotation.md)

## 의존성 조립

- [`providers/auth_provider.py`](providers/auth_provider.md)
