# `app/dialogue/model_loading.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/dialogue/model_loading.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 88줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

대화 모델 파일을 검사하고 CUDA에 양자화 모델을 불러온다.

## 함께 읽을 코드

- [app/config.py](../config.md)

## `validate_model_files`

[소스 선언 위치](../../../../app/dialogue/model_loading.py#L6)

```python
def validate_model_files(settings: Settings) -> None:
    ...
```

로컬 모델 및 선택한 어댑터 파일의 존재를 확인한다. 네트워크 다운로드는 하지 않는다.

**파라미터**

- settings (Settings): 모델 실행과 검색에 사용할 설정.

**반환값**

None: 반환값 없음.

## `load_model`

[소스 선언 위치](../../../../app/dialogue/model_loading.py#L42)

```python
def load_model(settings):
    ...
```

CUDA에서 NF4 + double quantization으로 로딩한다. 어댑터가 없으면 기본 모델이다.

**파라미터**

- settings: 모델 실행과 검색에 사용할 설정.

**반환값**

tuple: CUDA에 불러온 4비트 모델과 해당 모델의 토크나이저.
