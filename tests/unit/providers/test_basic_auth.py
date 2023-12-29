# pylint: disable=redefined-outer-name

"""This is a test to check if the Basic authentication is working."""


import pytest
import requests
from pytest_mock import MockerFixture

from multiauth.entities.main import AuthTech
from multiauth.entities.user import MethodName, UserName
from multiauth.manager import User
from multiauth.providers.basic import basic_authenticator


@pytest.fixture()
def auth_schema() -> dict:
    """Test auth schema."""

    return {'tech': 'basic'}


@pytest.fixture()
def user_config() -> User:
    """Test user configuration."""

    return User(
        name=UserName('fixture'),
        auth_schema=MethodName('schema1'),
        auth_tech=AuthTech.BASIC,
        auth_type=None,
        credentials={'username': 'postman', 'password': 'password'},
        token=None,
        refresh_token=None,
        expires_in=None,
        expired_token=None,
        token_info=None,
    )


def test_basic_authentication(mocker: MockerFixture, user_config: User, auth_schema: dict) -> None:
    """Function that makes the test on the basic authentication."""

    auth_response = basic_authenticator(user_config, auth_schema)

    assert auth_response.headers['Authorization'] == 'Basic cG9zdG1hbjpwYXNzd29yZA=='

    mocker.patch('requests.get', return_value=mocker.Mock(text='{"authenticated":true}'))

    response = requests.get(
        'http://example.com',
        headers=auth_response.headers,
        timeout=5,
    )

    assert response.text == '{"authenticated":true}'
