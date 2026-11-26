# `tests/investigation/data_helpers.py`

[코드 참조 목차](../../README.md) · [테스트 목차](../README.md) · [실제 소스](../../../../tests/investigation/data_helpers.py)

회귀 검사에서 정적 사건 JSON을 읽는다.

## `read`

[소스 선언](../../../../tests/investigation/data_helpers.py#L10)

```python
def read(name):
    ...
```

외부 Next.js가 아닌 프로젝트에 복사된 실제 데이터만 읽는다.

**인자**

- name: 읽을 파일 또는 실행할 사례의 이름.

**반환값**

- dict: 지정한 사건 JSON 파일에서 읽은 데이터.
