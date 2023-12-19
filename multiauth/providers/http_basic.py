"""Implementation of the Rest authentication schema."""


import base64

from multiauth.entities.errors import AuthenticationError
from multiauth.entities.providers.http import BasicCredentials, Credentials
from multiauth.providers.http_parser import parse_credentials


def basic_parse_credentials(schema: dict) -> BasicCredentials:
    """Parse a raw dictionary to GraphQLCredentials."""

    credentials = parse_credentials(schema)

    if 'username' not in schema:
        raise AuthenticationError('Mandatory `username` key is missing from Basic credentials')

    if not isinstance(schema['username'], str):
        raise AuthenticationError('`username` must be a string in Basic credentials')

    if 'password' not in schema:
        raise AuthenticationError('Mandatory `password` key is missing from Basic credentials')

    if not isinstance(schema['password'], str):
        raise AuthenticationError('`password` must be a string in Basic credentials')

    return BasicCredentials(
        name=credentials.name,
        headers=credentials.headers,
        cookies=credentials.cookies,
        body=credentials.body,
        username=schema['username'],
        password=schema['password'],
    )


def basic_to_standard_crendentials(credentials: BasicCredentials) -> Credentials:
    """Basic Authentication"""

    value = credentials.username + ':' + credentials.password

    # Encode base64 the value
    encoded_value = base64.b64encode(value.encode('ascii'))
    header_value = encoded_value.decode('ascii')

    return Credentials(
        name=credentials.name,
        headers=credentials.headers | {'Authorization': 'Basic ' + header_value},
        cookies=credentials.cookies,
        body=credentials.body,
    )
