"""같은 수사 요청을 식별하는 해시를 계산한다."""

import hashlib
import json


def digest(value) -> str:
    """JSON 내용을 정규화해 같은 요청인지 비교한다.

    Args:
        value: 요청을 구분하는 키와 본문.

    Returns:
        str: 같은 JSON 입력을 비교할 SHA-256 해시.
    """
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
