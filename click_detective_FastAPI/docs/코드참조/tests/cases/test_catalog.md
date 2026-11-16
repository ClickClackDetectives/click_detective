# `tests/cases/test_catalog.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/cases/test_catalog.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 110줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

cases/test_catalog.py의 회귀 동작을 확인한다.

## `test_public_data_and_assets`

[소스 선언 위치](../../../../tests/cases/test_catalog.py#L9)

```python
def test_public_data_and_assets(api):
    ...
```

사건·프로필·소개 자산은 조회하고 비공개 정답·증거 이미지는 막는다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_game_ownership_and_hidden_content`

[소스 선언 위치](../../../../tests/cases/test_catalog.py#L38)

```python
def test_game_ownership_and_hidden_content(api, game):
    ...
```

게임 ID를 알아도 토큰 없이 읽지 못하고 미열람 본문도 제공하지 않는다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_create_idempotency_and_conflict`

[소스 선언 위치](../../../../tests/cases/test_catalog.py#L66)

```python
def test_create_idempotency_and_conflict(api):
    ...
```

생성 요청을 재전송해도 같은 수사·토큰을 반환하고 다른 내용은 충돌한다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.

## `test_authentication`

[소스 선언 위치](../../../../tests/cases/test_catalog.py#L97)

```python
def test_authentication(api, path):
    ...
```

데이터·자산도 서버 전용 서비스 인증을 요구한다.

**파라미터**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- path: 저장 파일 경로나 HTTP 요청 경로.

**반환값**

None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
