"""Implementation of the Manual authentication schema."""

from typing import Any, cast

from multiauth.manager import User
from multiauth.types.errors import AuthenticationError
from multiauth.types.main import AuthResponse, AuthTech


def manual_authenticator(user: User) -> AuthResponse:
    """This function implements the Manual Authentication Schema.

    It simply take the headers that are found in the user credentials and puts them in the AuthResponse.
    """

    auth_response = AuthResponse({
        'headers': {},
        'tech': AuthTech.MANUAL,
    })

    headers = user.headers
    if not headers:
        if not user.credentials:
            raise AuthenticationError('Configuration file error. Missing credentials')
        if 'headers' not in user.credentials:
            raise AuthenticationError('Please input the necessary authentication headers.')

        headers = user.credentials['headers']

    auth_response['headers'] = cast(dict[str, Any], headers)
    auth_response['tech'] = AuthTech.MANUAL

    return auth_response
