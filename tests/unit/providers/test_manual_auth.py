# pylint: disable=redefined-outer-name

"""Basic example of what a developper would do to start a flow."""

from typing import Dict

import pytest

from multiauth import MultiAuth
from multiauth.providers.manual import manual_authenticator


@pytest.fixture()
def auth() -> Dict:
    """Return a fixture of schemas."""

    return {
        'manual_headers': {
            'tech': 'manual',
        },
    }


@pytest.fixture()
def users_one_header() -> Dict:
    """Return a fixture of users."""

    return {
        'manual_user': {
            'auth': 'manual_headers',
            'headers': {'Authorization': 'Bearer 12345'},
        },
    }


@pytest.fixture()
def users_two_headers() -> Dict:
    """Return a fixture of users."""

    return {
        'manual_user': {
            'auth': 'manual_headers',
            'headers': {'Authorization': 'Bearer 12345', 'Content-Type': 'application/json'},
        },
    }


def test_manual_authentication_headers(
    users_one_header: Dict,
    auth: Dict,
) -> None:
    """Test manual authentication."""

    instance = MultiAuth(auth, users_one_header)
    instance.authenticate_users()

    assert instance.headers['manual_user']['Authorization'] == 'Bearer 12345'

    headers, _ = instance.authenticate('manual_user')

    assert len(headers) == 1
    assert headers['Authorization'] == 'Bearer 12345'


def test_manual_authentication_credentials(
    users_two_headers: Dict,
    auth: Dict,
) -> None:
    """Test manual authentication."""

    instance = MultiAuth(auth, users_two_headers)
    instance.authenticate_users()

    assert instance.headers['manual_user']['Authorization'] == 'Bearer 12345'

    headers, _ = instance.authenticate('manual_user')

    assert len(headers) == 2
    assert headers['Authorization'] == 'Bearer 12345'
    assert headers['Content-Type'] == 'application/json'


def test_manual_handler_headers(
    users_one_header: Dict,
    auth: Dict,
) -> None:
    """Test manual handler."""

    auth_response = manual_authenticator(MultiAuth.serialize_users(auth, users_one_header)['manual_user'])

    assert auth_response['headers']['Authorization'] == 'Bearer 12345'
