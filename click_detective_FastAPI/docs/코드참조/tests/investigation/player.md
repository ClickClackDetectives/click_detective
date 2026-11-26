# `tests/investigation/player.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/investigation/player.py)

사용자 행동 API로만 수사를 진행하는 테스트 도우미다.

## `Player`

[소스 선언](../../../../tests/investigation/player.py#L6)

```python
class Player:
    ...
```

게임 상태를 조작하지 않고 사용자 행동 API로만 진행한다.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

**반환값**

- Player: 위 역할을 수행하도록 생성된 객체.

## `Player.__init__`

[소스 선언](../../../../tests/investigation/player.py#L17)

```python
def __init__(self, api, game):
    ...
```

API와 초기 수사 상태를 보관한다.

**인자**

- api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.
- game: 테스트에서 생성한 수사의 ID, 토큰과 상태.

**반환값**

- None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.

## `Player.act`

[소스 선언](../../../../tests/investigation/player.py#L32)

```python
def act(self, endpoint, **fields):
    ...
```

새 요청 UUID·서버 revision을 넣고 갱신 상태를 적용한다.

**인자**

- endpoint: 요청할 수사 행동 API의 마지막 경로.
- fields: 행동 요청에 추가할 입력 필드.

**반환값**

- dict: 행동의 결과와 최신 공개 상태. 도우미가 보관한 상태도 갱신한다.
