# `app/investigation/timeline.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/investigation/timeline.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 99줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

확보한 진술과 문서로 공개 시간표를 구성한다.

## `build_timeline`

[소스 선언 위치](../../../../app/investigation/timeline.py#L6)

```python
def build_timeline(catalog, state):
    ...
```

실제 확보한 진술·문서만 공개 시간표에 추가한다. 숨겨진 실제 행적은 사용하지 않는다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- state: 질문·대화·획득 자료를 담은 현재 수사 상태.

**반환값**

list[dict]: 공개된 자료로 구성하여 시작 시각·ID 순으로 정렬한 시간표.
