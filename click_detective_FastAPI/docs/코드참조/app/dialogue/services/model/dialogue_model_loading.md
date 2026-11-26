# `app/dialogue/services/model/dialogue_model_loading.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/dialogue/services/model/dialogue_model_loading.py)

CUDA에 양자화 모델과 토크나이저를 불러온다.

## `load_model`

[소스 선언](../../../../../../app/dialogue/services/model/dialogue_model_loading.py#L8)

```python
def load_model(settings):
    ...
```

CUDA에서 NF4 + double quantization으로 로딩한다. 어댑터가 없으면 기본 모델이다.

**인자**

- settings: 모델 실행과 검색에 사용할 설정.

**반환값**

- tuple: CUDA에 불러온 4비트 모델과 해당 모델의 토크나이저.
