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

    print('#' * 80)
    print(user)

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


def serialize_headers_to_manual(headers: dict[str, str] | list[str] | str) -> tuple[dict, dict]:
    """Serialize raw headers in "manual" auth format."""

    headers_dict: dict[str, str] = {}

    if isinstance(headers, str):
        headers = [headers]

    if isinstance(headers, list):

        for header in headers:
            header_split = header.split(':')
            header_name = header_split[0].strip()
            header_value = ':'.join(header_split[1:]).strip()
            headers_dict[header_name] = header_value

    elif isinstance(headers, dict):
        headers_dict = headers

    auth_name = 'manual_headers'

    auths: dict = {
        auth_name: {
            'tech': AuthTech.MANUAL,
        },
    }

    users: dict = {
        'manual_user': {
            'headers': headers_dict,
            'auth': auth_name
        },
    }

    return auths, users
