"""수사 데이터베이스의 연결과 트랜잭션 수명을 관리한다."""

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class InvestigationStorage:
    """수사 데이터베이스의 연결을 제공한다.

    Args:
        path (Path): 저장 파일 경로나 HTTP 요청 경로.

    Returns:
        InvestigationStorage: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, path: Path):
        """접근할 데이터베이스 경로를 보관한다.

        Args:
            path (Path): 저장 파일 경로나 HTTP 요청 경로.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.path = path

    @contextmanager
    def transaction(self):
        """짧은 쓰기 트랜잭션을 제공한다. 실패 시 롤백하고 연결을 항상 닫는다.

        Args:
            없음.

        Returns:
            ContextManager: SQLite 연결을 제공하고 성공 시 commit, 실패 시 rollback하는 문맥 관리자.
        """
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()


def digest(value) -> str:
    """JSON 내용을 정규화해 같은 요청인지 비교한다. 값은 SQL에 바인딩한다.

    Args:
        value: 검사·변환하거나 비밀값을 가릴 입력 값.

    Returns:
        str: 같은 JSON 입력을 비교할 SHA-256 해시.
    """
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
