# pylint: disable=redefined-outer-name, no-self-use

"""This is a test to check if the Basic authentication is working."""

from typing import Dict

import pytest
import requests
from pytest_mock import MockerFixture

from multiauth.entities.main import AuthTech
from multiauth.manager import User
from multiauth.providers.basic import basic_authenticator


@pytest.fixture
def auth_schema() -> Dict:
    """Test auth schema."""

    return {'tech': 'basic'}


@pytest.fixture
def user_config() -> User:
    """Test user configuration."""

    return User({
        'auth_schema': 'schema1',
        'auth_tech': AuthTech.BASIC,
        'auth_type': None,
        'credentials': {
            'username': 'postman',
            'password': 'password'
        },
        'token': None,
        'refresh_token': None,
        'expires_in': None,
        'expired_token': None,
        'token_info': None,
    })


def test_basic_authentication(mocker: MockerFixture, user_config: User, auth_schema: Dict) -> None:
    """Function that makes the test on the basic authentication."""

    auth_response = basic_authenticator(user_config, auth_schema)

    assert auth_response['headers']['Authorization'] == 'Basic cG9zdG1hbjpwYXNzd29yZA=='

    mocker.patch('requests.get', return_value=mocker.Mock(text='{"authenticated":true}'))

    response = requests.get(
        'http://example.com',
        headers=auth_response['headers'],
    )

    assert response.text == '{"authenticated":true}'
