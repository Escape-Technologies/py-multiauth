"""Implementation of the API Key authentication schema."""

from typing import Dict, cast

from multiauth.entities.errors import AuthenticationError
from multiauth.entities.http import Location
from multiauth.entities.main import AuthConfigApiKey, AuthResponse, AuthTech
from multiauth.manager import User


def apikey_config_parser(schema: Dict) -> AuthConfigApiKey:
    """This function parses the API Key schema and checks if all necessary fields exist."""

    auth_config = AuthConfigApiKey(
        {
            'location': Location.HEADERS,
            'header_name': '',
            'header_prefix': None,
            'headers': None,
        },
    )

    if not schema.get('header_name'):
        raise AuthenticationError('Please provide the key of the API Authentication')
    if not schema.get('location'):
        raise AuthenticationError('Please provide the location to where you want to add the API Key')

    auth_config['header_name'] = cast(str, schema.get('header_name'))
    auth_config['location'] = schema['location']

    if 'options' in schema:
        auth_config['header_prefix'] = schema['options'].get('header_prefix', 'Authorization')
        auth_config['headers'] = schema['options'].get('headers')

    return auth_config


def apikey_auth_attach(
    user: User,
    auth_config: AuthConfigApiKey,
) -> AuthResponse:
    """This function attaches the user credentials to the schema and generates the proper authentication response."""

    auth_response = AuthResponse(
        {
            'headers': {},
            'tech': AuthTech.APIKEY,
        },
    )

    # First take the credentials from the user
    if not user.credentials:
        raise AuthenticationError('Configuration file error. Missing credentials')
    if not user.credentials.get('api_key'):
        raise AuthenticationError("Failed to fetch user's API Key")

    api_key: str = user.credentials['api_key']

    # Add the token to the current user
    user.set_token(api_key, None)

    # Implementation with no expression matching in order to work with mypy
    if auth_config['location'] == Location.HEADERS:
        if auth_config['header_prefix'] is not None:
            auth_response['headers'][auth_config['header_name']] = auth_config['header_prefix'] + ' ' + api_key
        else:
            auth_response['headers'][auth_config['header_name']] = api_key

    if auth_config['location'] == Location.URL:
        pass

    # Append the optional headers to the header
    if auth_config['headers'] is not None:
        for name, value in auth_config['headers'].items():
            # Resolving duplicate keys
            if name in auth_response['headers']:
                auth_response['headers'][name] += ', ' + value

            else:
                auth_response['headers'][name] = value

    return auth_response


def apikey_authenticator(
    user: User,
    schema: Dict,
) -> AuthResponse:
    """This funciton is a wrapper function that implements the API Key authentication schema.

    It simply takes the API key from the user and addes the api key either to the header of the HTTP request or as a parameter of the URL
    """

    auth_config = apikey_config_parser(schema)
    return apikey_auth_attach(user, auth_config)
