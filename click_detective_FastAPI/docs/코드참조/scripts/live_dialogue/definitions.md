# `scripts/live_dialogue/definitions.py`

[코드 참조 목차](../../README.md) · [스크립트 목차](../README.md) · [실제 소스](../../../../scripts/live_dialogue/definitions.py)

사건 데이터에서 실서버 대화 검사 입력을 고른다.

## `definitions`

[소스 선언](../../../../scripts/live_dialogue/definitions.py#L8)

```python
def definitions(catalog, data_dir):
    ...
```

현재 프로젝트의 인물·주제·1차 단일 근거 쟁점으로 3가지 입력을 구성한다.

**인자**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- data_dir: 사건 JSON 데이터가 있는 디렉터리.

**반환값**

- dict: profile, movement, evidence 세 가지 심문 사례.
