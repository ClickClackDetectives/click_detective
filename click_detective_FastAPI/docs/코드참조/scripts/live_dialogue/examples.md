# `scripts/live_dialogue/examples.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../scripts/live_dialogue/examples.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 93줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

실제 인물과 사건 자료로 130개 질문을 구성한다.

## `definitions`

[소스 선언 위치](../../../../scripts/live_dialogue/examples.py#L12)

```python
def definitions(catalog):
    ...
```

실제 인물·주제·추천 질문·1차 자료를 이용해 인물당 26개를 만든다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

**반환값**

list[dict]: 인물별 질문과 준비 자료로 구성한 130개 실행 사례.
