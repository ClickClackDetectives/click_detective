# `scripts/run_130_live_examples.py`

[코드 참조 목차](../README.md) · [스크립트 목차](README.md) · [실제 소스](../../../scripts/run_130_live_examples.py)

실행 중인 서버에 130개 대화 사례를 순서대로 요청한다.

## `main`

[소스 선언](../../../scripts/run_130_live_examples.py#L20)

```python
def main():
    ...
```

한 서버에 순차 요청하여 GPU 모델 중복 로딩과 동시 부하를 피한다.

**인자**

- 없음.

**반환값**

- int: 성공은 0, 검사 실패는 1. 잘못된 설정은 파서가 오류로 종료한다.
