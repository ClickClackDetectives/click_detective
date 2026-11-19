# `tests/investigation/data_helpers.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../tests/investigation/data_helpers.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 19줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

회귀 검사에서 정적 사건 JSON을 읽는다.

## 함께 읽을 코드

- [app/config.py](../../app/config.md)

## `read`

[소스 선언 위치](../../../../tests/investigation/data_helpers.py#L10)

```python
def read(name):
    ...
```

외부 Next.js가 아닌 프로젝트에 복사된 실제 데이터만 읽는다.

**파라미터**

- name: 읽을 파일 또는 실행할 사례의 이름.

**반환값**

dict: 지정한 사건 JSON 파일에서 읽은 데이터.
