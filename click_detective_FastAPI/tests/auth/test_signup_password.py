"""회원가입의 비밀번호 길이와 문자 조합을 검사한다."""

import pytest
from fastapi import HTTPException

from tests.auth.test_auth_contract import auth as auth


def test_signup_requires_length_and_all_character_types(auth):
    """가입 비밀번호에는 8~16자와 영문, 숫자, 특수문자가 필요하다.

    Args:
        auth: 임시 PostgreSQL에 연결한 실제 인증 서비스.

    Returns:
        None: 정책 위반과 양쪽 길이 경계에서의 가입 결과를 검사한다.
    """
    invalid = [
        "abcd1!x",
        "abcdefghijklmn1!x",
        "ABCDEFG!",
        "abcdefg1",
        "1234567!",
    ]
    for password in invalid:
        with pytest.raises(HTTPException) as failure:
            auth.signup("invalid@example.com", password)
        assert failure.value.status_code == 422
        assert failure.value.detail["code"] == "INVALID_PASSWORD"

    assert auth.signup("lower@example.com", "abcdef1!")["email"] == "lower@example.com"
    assert (
        auth.signup("upper@example.com", "ABCDEFGHIJKLMN2#")["email"]
        == "upper@example.com"
    )
