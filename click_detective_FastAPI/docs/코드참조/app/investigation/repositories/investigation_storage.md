# `app/investigation/repositories/investigation_storage.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/repositories/investigation_storage.py)

같은 수사 요청을 식별하는 해시를 계산한다.

## `digest`

[소스 선언](../../../../../app/investigation/repositories/investigation_storage.py#L7)

```python
def digest(value) -> str:
    ...
```

JSON 내용을 정규화해 같은 요청인지 비교한다.

**인자**

- value: 요청을 구분하는 키와 본문.

**반환값**

- str: 같은 JSON 입력을 비교할 SHA-256 해시.
