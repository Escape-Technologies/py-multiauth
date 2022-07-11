# pylint: disable=line-too-long, redefined-outer-name

"""Test expired token behaviour."""

import pytest

from multiauth.manager import User
from multiauth.types.errors import ExpiredTokenError


@pytest.fixture
def expired_token() -> str:
    """Fixture an expired token."""

    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjEyMzQ1fQ.xVG1HwFudlbhyP0lN211c8L5UZ5oPxLjSDKYOzYSmyk'


def test_user_with_expired_token(expired_token: str) -> None:
    """Test instance of User with expired token."""

    try:
        _user = User({
            'token': expired_token,
        })
        assert False

    except ExpiredTokenError:
        assert True


def test_user_with_expired_refresh_token(expired_token: str) -> None:
    """Test instance of User with expired token."""

    try:
        _user = User({
            'refresh_token': expired_token,
        })
        assert False

    except ExpiredTokenError:
        assert True
