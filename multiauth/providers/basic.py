"""Implementation of the API Key authentication schema."""

import base64
from typing import Dict

from multiauth.entities.main import AuthResponse, AuthTech
from multiauth.manager import User


def basic_authenticator(
    user: User,
    schema: Dict,
) -> AuthResponse:
    """This function implement the `Basic Authentication` Schema.

    It simply takes the username and password from the current working user, appends the password to the username, and base64 encode them. Finally it adds them
    to the authentication header in the HTTP request
    """

    auth_response = AuthResponse(
        {
            'headers': {},
            'tech': AuthTech.BASIC,
        },
    )

    # Take the username and password from the user in the configuration file
    username, password = user.get_credentials_pair()

    value = username + ':' + password
    # Encode base64 the value
    encoded_value = base64.b64encode(value.encode('ascii'))
    header_value = encoded_value.decode('ascii')

    # Add the token to the current user
    user.set_token(header_value, None)

    auth_response['headers']['Authorization'] = 'Basic ' + header_value

    if 'options' not in schema:
        return auth_response

    # Append the optional headers to the header
    headers = schema['options'].get('headers')
    if headers:
        for name, value in headers.items():
            # Resolving duplicate keys
            if name in auth_response['headers']:
                auth_response['headers'][name] += ', ' + value
            else:
                auth_response['headers'][name] = value

    return auth_response
