# pylint: disable=line-too-long, redefined-outer-name

"""Test expired token behaviour."""

import pytest

from multiauth.entities.errors import ExpiredTokenError
from multiauth.entities.main import Token
from multiauth.entities.user import UserName
from multiauth.manager import User


@pytest.fixture()
def expired_token() -> Token:
    """Fixture an expired token."""

    return Token(
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjEyMzQ1fQ.xVG1HwFudlbhyP0lN211c8L5UZ5oPxLjSDKYOzYSmyk',
    )


def test_user_with_expired_token(expired_token: Token) -> None:
    """Test instance of User with expired token."""

    try:
        _user = User(name=UserName('user'), token=expired_token)
        raise AssertionError

    except ExpiredTokenError:
        assert True


def test_user_with_expired_refresh_token(expired_token: Token) -> None:
    """Test instance of User with expired token."""

    try:
        _user = User(name=UserName('user'), refresh_token=expired_token)
        raise AssertionError

    except ExpiredTokenError:
        assert True
