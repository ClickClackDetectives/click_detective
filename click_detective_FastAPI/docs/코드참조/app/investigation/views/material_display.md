# `app/investigation/views/material_display.py`

[코드 참조 목차](../../../README.md) · [전체 문서 목차](../../../../README.md) · [실제 소스](../../../../../app/investigation/views/material_display.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 91줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

획득한 출처를 화면에서 선택할 수 있는 설명으로 바꾼다.

## `describe_source`

[소스 선언 위치](../../../../../app/investigation/views/material_display.py#L4)

```python
def describe_source(catalog, state, ref):
    ...
```

실제 획득 출처를 화면용 번호·제목·분류로 바꾼다.

**파라미터**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- ref: 자료 종류와 식별자를 담은 출처 참조.

**반환값**

dict: 출처의 번호·제목·분류와 설명.

## `list_materials`

[소스 선언 위치](../../../../../app/investigation/views/material_display.py#L46)

```python
def list_materials(catalog, state):
    ...
```

현재 수사에서 볼 수 있는 원본·진술·추론의 목록을 만든다.

**파라미터**

- catalog: 원본 증거를 담은 사건 데이터.
- state: 현재 조사 단계와 획득 자료를 담은 수사 상태.

**반환값**

list[dict]: 화면에 공개할 자료의 제목·요약·획득 여부.
