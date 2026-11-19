# `scripts/live_dialogue/definitions.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../scripts/live_dialogue/definitions.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 77줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

사건 데이터에서 실서버 대화 검사 입력을 고른다.

## 함께 읽을 코드

- [scripts/live_dialogue/errors.py](errors.md)

## `definitions`

[소스 선언 위치](../../../../scripts/live_dialogue/definitions.py#L8)

```python
def definitions(catalog, data_dir):
    ...
```

현재 프로젝트의 인물·주제·1차 단일 근거 쟁점으로 3가지 입력을 구성한다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- data_dir: 사건 JSON 데이터가 있는 디렉터리.

**반환값**

dict: profile, movement, evidence 세 가지 심문 사례.
