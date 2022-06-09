# pylint: disable=redefined-outer-name

"""Basic example of what a developper would do to start a flow."""

import pytest

from multiauth import MultiAuth, User
from multiauth.providers.manual import manual_authenticator


@pytest.fixture
def auth_schema() -> dict:
    """Return a fixture of schemas."""

    return {
        'manual_headers': {
            'tech': 'manual',
        },
    }


@pytest.fixture
def user_config() -> dict[str, User]:
    """Return a fixture of users."""

    return {
        'user_lambda': User({
            'auth_schema': 'manual_headers',
            'credentials': {
                'headers': {
                    'Authorization': 'Bearer 12345'
                }
            },
        }),
    }


def test_manual_authentication(user_config: dict[str, User], auth_schema: dict) -> None:
    """Test manual authentication."""

    instance = MultiAuth(auth_schema, user_config)
    instance.authenticate_users()

    assert instance.headers['user_lambda']['Authorization'] == 'Bearer 12345'

    headers, _ = instance.authenticate('user_lambda')
    assert headers['Authorization'] == 'Bearer 12345'


def test_manual_handler(user_config: dict[str, User]) -> None:
    """Test manual handler."""

    auth_response = manual_authenticator(user_config['user_lambda'])

    assert auth_response['headers']['Authorization'] == 'Bearer 12345'
