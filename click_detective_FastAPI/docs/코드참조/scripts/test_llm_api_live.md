# `scripts/test_llm_api_live.py`

[코드 참조 목차](../README.md) · [스크립트 목차](README.md) · [실제 소스](../../../scripts/test_llm_api_live.py)

실행 중인 FastAPI 대화 경로를 HTTP로 검사하는 명령행 진입점이다.

## `parser`

[소스 선언](../../../scripts/test_llm_api_live.py#L28)

```python
def parser():
    ...
```

비밀 키는 명령행 인수가 아닌 환경변수 또는 .env에서만 읽는다.

**인자**

- 없음.

**반환값**

- argparse.ArgumentParser: 실서버 검사에 사용할 명령행 인수 파서.

## `main`

[소스 선언](../../../scripts/test_llm_api_live.py#L79)

```python
def main(argv=None):
    ...
```

실행 결과를 JSON으로 저장하고 성공 0·실패 1·설정 오류 2를 반환한다.

POSIX에서는 결과 파일 권한을 600으로 제한한다.

**인자**

- argv: 명령행 인수 목록. None이면 실제 명령행에서 읽는다.

**반환값**

- int: 성공은 0, 검사 실패는 1. 잘못된 설정은 파서가 오류로 종료한다.
