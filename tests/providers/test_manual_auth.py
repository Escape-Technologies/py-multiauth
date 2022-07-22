# pylint: disable=redefined-outer-name

"""Basic example of what a developper would do to start a flow."""

from typing import Dict

import pytest

from multiauth import MultiAuth
from multiauth.providers.manual import manual_authenticator


@pytest.fixture
def auth() -> Dict:
    """Return a fixture of schemas."""

    return {
        'manual_headers': {
            'tech': 'manual',
        },
    }


@pytest.fixture
def user_config_credentials() -> Dict:
    """Return a fixture of users."""

    return {
        'user_lambda': {
            'auth': 'manual_headers',
            'headers': {
                'Authorization': 'Bearer 12345'
            },
        }
    }


@pytest.fixture
def user_config_headers() -> Dict:
    """Return a fixture of users."""

    return {
        'user_lambda': {
            'auth': 'manual_headers',
            'headers': {
                'Authorization': 'Bearer 12345'
            }
        },
    }


def test_manual_authentication_credentials(user_config_credentials: Dict, auth: Dict) -> None:
    """Test manual authentication."""

    instance = MultiAuth(auth, user_config_credentials)
    instance.authenticate_users()

    assert instance.headers['user_lambda']['Authorization'] == 'Bearer 12345'

    headers, _ = instance.authenticate('user_lambda')
    assert headers['Authorization'] == 'Bearer 12345'


def test_manual_authentication_headers(user_config_headers: Dict, auth: Dict) -> None:
    """Test manual authentication."""

    instance = MultiAuth(auth, user_config_headers)
    instance.authenticate_users()

    assert instance.headers['user_lambda']['Authorization'] == 'Bearer 12345'

    headers, _ = instance.authenticate('user_lambda')
    assert headers['Authorization'] == 'Bearer 12345'


def test_manual_handler_credentials(user_config_credentials: Dict, auth: Dict) -> None:
    """Test manual handler."""

    auth_response = manual_authenticator(MultiAuth.serialize_users(auth, user_config_credentials)['user_lambda'])

    assert auth_response['headers']['Authorization'] == 'Bearer 12345'


def test_manual_handler_headers(user_config_headers: Dict, auth: Dict) -> None:
    """Test manual handler."""

    auth_response = manual_authenticator(MultiAuth.serialize_users(auth, user_config_headers)['user_lambda'])

    assert auth_response['headers']['Authorization'] == 'Bearer 12345'
