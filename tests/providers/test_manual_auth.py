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
def user_config_credentials() -> dict[str, User]:
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


@pytest.fixture
def user_config_headers() -> dict[str, User]:
    """Return a fixture of users."""

    return {
        'user_lambda': User({
            'auth_schema': 'manual_headers',
            'headers': {
                'Authorization': 'Bearer 12345'
            }
        }),
    }


def test_manual_authentication_credentials(user_config_credentials: dict[str, User], auth_schema: dict) -> None:
    """Test manual authentication."""

    instance = MultiAuth(auth_schema, user_config_credentials)
    instance.authenticate_users()

    assert instance.headers['user_lambda']['Authorization'] == 'Bearer 12345'

    headers, _ = instance.authenticate('user_lambda')
    assert headers['Authorization'] == 'Bearer 12345'


def test_manual_authentication_headers(user_config_headers: dict[str, User], auth_schema: dict) -> None:
    """Test manual authentication."""

    instance = MultiAuth(auth_schema, user_config_headers)
    instance.authenticate_users()

    assert instance.headers['user_lambda']['Authorization'] == 'Bearer 12345'

    headers, _ = instance.authenticate('user_lambda')
    assert headers['Authorization'] == 'Bearer 12345'


def test_manual_handler_credentials(user_config_credentials: dict[str, User]) -> None:
    """Test manual handler."""

    auth_response = manual_authenticator(user_config_credentials['user_lambda'])

    assert auth_response['headers']['Authorization'] == 'Bearer 12345'


def test_manual_handler_headers(user_config_headers: dict[str, User]) -> None:
    """Test manual handler."""

    auth_response = manual_authenticator(user_config_headers['user_lambda'])

    assert auth_response['headers']['Authorization'] == 'Bearer 12345'
