# `tests/test_code_conventions.py`

[코드 참조 목차](../README.md) · [테스트 목차](README.md) · [실제 소스](../../../tests/test_code_conventions.py)

파일 길이와 설명서 형식이 이후 변경에서도 유지되는지 검사한다.

## `python_sources`

[소스 선언](../../../tests/test_code_conventions.py#L10)

```python
def python_sources():
    ...
```

프로젝트가 관리하는 Python 파일만 모은다.

**인자**

- 없음.

**반환값**

- list[Path]: 가상환경을 제외한 app, scripts, tests의 Python 파일 목록.

## `test_each_python_file_has_at_most_250_lines`

[소스 선언](../../../tests/test_code_conventions.py#L26)

```python
def test_each_python_file_has_at_most_250_lines():
    ...
```

빈 줄과 docstring을 포함해 파일당 250줄 제한을 검사한다.

**인자**

- 없음.

**반환값**

- None: 길이 제한을 넘는 파일이 있으면 assertion으로 경로와 줄 수를 표시한다.

## `test_classes_and_functions_document_parameters_and_returns`

[소스 선언](../../../tests/test_code_conventions.py#L43)

```python
def test_classes_and_functions_document_parameters_and_returns():
    ...
```

모든 클래스·함수의 역할, 파라미터와 반환값 설명을 확인한다.

**인자**

- 없음.

**반환값**

- None: 설명이 누락되면 해당 파일과 선언문의 이름을 표시한다.
