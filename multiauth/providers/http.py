"""Implementation of the Rest authentication schema."""

from typing import Any, Dict

from requests import Response, request

from multiauth.entities.errors import AuthenticationError
from multiauth.entities.main import AuthResponse, AuthTech
from multiauth.entities.providers.http import (
    AuthProvider,
    AuthRequester,
    Credentials,
)
from multiauth.manager import User
from multiauth.providers.http_parser import parse_config


def attach_auth(
    user: User,
    auth_config: AuthProvider,
    proxy: str | None = None,
) -> AuthResponse:
    """This function takes the credentials of the user and authenticates them on the authentication URL."""

    if user and auth_config and proxy:  # TODO(antoine@escape.tech): remove this and code the function
        raise AuthenticationError('Cannot use proxy with user credentials')

    return AuthResponse(tech=AuthTech.REST, headers={})


def http_authenticator(
    user: User,
    schema: Dict,
    proxy: str | None = None,
) -> AuthResponse:
    """This funciton is a wrapper function that implements the Rest authentication schema.

    It takes the credentials of the user and authenticates them on the authentication URL.
    After authenticating, it fetches the token and adds the token to the
    headers along with optional headers in case the user provided them.
    """

    auth_config = parse_config(schema)
    return attach_auth(user, auth_config, proxy=proxy)


def merge_data(base_data: Any, user_data: Any) -> Any:
    # If the base data is a dict, and the user data is a dict, then we merge them
    if isinstance(base_data, dict) and isinstance(user_data, dict):
        return base_data | user_data

    # If the base data is a list, and the user data is a list, then we merge them
    if isinstance(base_data, list) and isinstance(user_data, list):
        return base_data + user_data

    if user_data is None:
        return base_data

    # In any other case, user_data prevails over base_data
    return user_data

def send_http_request(requester: AuthRequester, credential: Credentials) -> Response:
    url = requester.url
    method = requester.method

    headers = requester.headers | credential.headers
    cookies = requester.cookies | credential.cookies

    data = merge_data(requester.body, credential.body)

    return request(method, url, headers=headers, cookies=cookies, data=data)

