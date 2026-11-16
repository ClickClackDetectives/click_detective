"""회귀 검사에서 정적 사건 JSON을 읽는다."""

import json

from app.config import PROJECT_ROOT

DATA = PROJECT_ROOT / "data/case"


def read(name):
    """외부 Next.js가 아닌 프로젝트에 복사된 실제 데이터만 읽는다.

    Args:
        name: 읽을 파일 또는 실행할 사례의 이름.

    Returns:
        dict: 지정한 사건 JSON 파일에서 읽은 데이터.
    """
    return json.loads((DATA / name).read_text())
