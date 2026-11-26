# `app/dialogue/repositories/dialogue_model_file_repository.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/dialogue/repositories/dialogue_model_file_repository.py)

대화 모델과 어댑터의 로컬 파일을 확인한다.

## `validate_model_files`

[소스 선언](../../../../../app/dialogue/repositories/dialogue_model_file_repository.py#L6)

```python
def validate_model_files(settings: Settings) -> None:
    ...
```

로컬 모델 및 선택한 어댑터 파일의 존재를 확인한다. 네트워크 다운로드는 하지 않는다.

**인자**

- settings (Settings): 모델 실행과 검색에 사용할 설정.

**반환값**

- None: 반환값 없음.
