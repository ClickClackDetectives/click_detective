# `scripts/live_dialogue/examples.py`

[코드 참조 목차](../../README.md) · [스크립트 목차](../README.md) · [실제 소스](../../../../scripts/live_dialogue/examples.py)

실제 인물과 사건 자료로 130개 질문을 구성한다.

## `definitions`

[소스 선언](../../../../scripts/live_dialogue/examples.py#L12)

```python
def definitions(catalog):
    ...
```

실제 인물·주제·추천 질문·1차 자료를 이용해 인물당 26개를 만든다.

**인자**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

**반환값**

- list[dict]: 인물별 질문과 준비 자료로 구성한 130개 실행 사례.
