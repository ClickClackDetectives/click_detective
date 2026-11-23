# FastAPI 작업 규칙

- HTTP 입력·응답과 상태 코드는 `app/investigation/api/`의 기존 라우트와 스키마를 따른다. 라우트에서 호출하는 수사 흐름은 `app/investigation/service.py`의 구조를 따른다.
- 자료 공개, 진술 획득, 추론, 고발 판정은 `app/investigation/rules/`에 둔다. 조회 결과를 화면용으로 구성할 때는 `app/investigation/views/`의 기존 함수를 활용한다.
- SQLite 읽기·쓰기는 `app/investigation/persistence/`의 기존 경로를 사용한다. 변경 요청의 요청 식별자와 상태 버전 처리 방식을 유지한다.
- Python 포맷과 import 정리는 `pyproject.toml`의 Ruff 설정을 따른다. 테스트가 검사하는 함수·클래스에는 매개변수와 반환값을 기존 docstring 형식으로 설명한다.

## Python docstring

- 선언 바로 아래에 삼중 큰따옴표로 작성한다. 요약 뒤에 빈 줄을 두고 `Args:`, `Returns:` 순서로 적는다. 인자는 `이름: 설명`, 반환값은 `타입: 설명` 형식을 사용한다.
- `self`와 `cls`는 생략한다. 인자가 없으면 `Args:`에 `없음.`을, 반환값이 없으면 `Returns:`에 `None: 반환값 없음.`을 적는다. 비동기 함수는 await한 결과를 설명한다.
- 클래스 docstring에는 생성자 인자와 인스턴스의 역할을 적고, `__init__`에는 메서드 형식을 적용한다. 호출자가 처리해야 하는 예외는 `Returns:` 뒤의 `Raises:`에 발생 조건과 함께 적는다.
