"""Implementation of the Rest authentication schema."""

from typing import cast

import jwt
import requests

from multiauth.helpers import extract_token
from multiauth.manager import User
from multiauth.types.errors import AuthenticationError
from multiauth.types.main import AuthResponse, AuthTech
from multiauth.types.providers.rest import AuthConfigRest

# from escape_cli.common.user import USER_MANAGER


def rest_config_parser(schema: dict) -> AuthConfigRest:
    """This function parses the Rest schema and checks if all the necessary fields exist."""

    auth_config = AuthConfigRest({
        'url': '',
        'method': 'POST',
        'token_name': None,
        'cookie_auth': False,
        'refresh_url': None,
        'refresh_token_name': None,
        'header_name': None,
        'header_key': None,
        'headers': None,
    })

    if not schema.get('url'):
        raise AuthenticationError('Please provide the authentication URL')
    if not schema.get('method'):
        raise AuthenticationError('Please provide the HTTP method to use for authentication')

    auth_config['url'] = schema['url']
    auth_config['method'] = schema['method']

    # Options:
    if 'options' in schema:
        auth_config['cookie_auth'] = schema['options'].get('cookie_auth', False)
        if not auth_config['cookie_auth'] and not schema['options'].get('token_name'):
            raise AuthenticationError('Please provide the token name in the authentication response')

        auth_config['refresh_url'] = schema['options'].get('refresh_url')
        auth_config['refresh_token_name'] = schema['options'].get('refresh_token_name')
        auth_config['token_name'] = schema['options'].get('token_name')
        auth_config['header_name'] = schema['options'].get('header_name')
        auth_config['header_key'] = schema['options'].get('header_key')
        auth_config['headers'] = schema['options'].get('headers')

    return auth_config


#pylint: disable=too-many-branches
def rest_auth_attach(user: User, auth_config: AuthConfigRest) -> AuthResponse:
    """This function attaches the user credentials to the schema and generates the proper authentication response."""

    # First we have to take the credentials from the currently working user
    credentials = user.credentials
    if not credentials:
        raise AuthenticationError('Configuration file error. Missing credentials')

    # Now we need to send the request
    response = requests.request(auth_config['method'], auth_config['url'], json=credentials)
    # If there is a cookie that is fetched, added it to the auth response header
    cookie_header = response.cookies.get_dict()  # type: ignore[no-untyped-call]
    if cookie_header:
        cookie_header = [f'{name}={value}' for name, value in cookie_header.items()]
        cookie_header = ';'.join(cookie_header)
        if auth_config['cookie_auth'] and not cookie_header:
            raise AuthenticationError('Authentication Failed: No cookie was found')
    else:
        cookie_header = None

    # Prepare the header in order to fetch the token
    # We are creating a header for the token because the helper function '_extract_token' works like that
    headers: dict[str, str] = {}

    # Now we want to append the authentication headers
    # There are two parts
    # 1- If auth cookie is enabled, then we simply search add the cookie to the auth response and that is it
    # 2- If auth cookie is disables, we continue the authentication process
    if not auth_config['cookie_auth']:
        token_name = cast(str, auth_config['token_name'])
        if auth_config['header_name'] is None:
            headers['Authorization'] = ''
        else:
            headers[auth_config['header_name']] = ''

        if auth_config['header_key'] is not None:
            headers[next(iter(headers))] += auth_config['header_key'] + ' ' + '{{' + token_name + '}}'
        else:
            headers[next(iter(headers))] += 'Bearer {{' + token_name + '}}'

    # Append the optional headers to the header
    if auth_config['headers'] is not None:
        for name, value in auth_config['headers'].items():

            # Resolving duplicate keys
            if name in headers:
                headers[name] += ', ' + value

            else:
                headers[name] = value

    # Append the cookie header and check if the authentication type is a cookie authentication or no
    if cookie_header:
        headers['cookie'] = cookie_header
        if auth_config['cookie_auth']:
            return AuthResponse({
                'tech': AuthTech.REST,
                'headers': headers,
            })

    auth_response, refresh_token = extract_token(response, AuthTech.REST, headers, auth_config['refresh_token_name'])

    token = auth_response['headers'][next(iter(headers))].split(' ')[1]

    # Add the token and the expiry time to the user manager in order to be accessed by other parts of the program
    expiry_time: float | None = None
    try:
        expiry_time = jwt.decode(token, options={
            'verify_signature': False,
            'verify_exp': True,
        }).get('exp')
    except jwt.exceptions.DecodeError:
        pass
    finally:
        user.set_token(token, expiry_time)

    user.refresh_token = refresh_token

    return auth_response


def rest_authenticator(user: User, schema: dict) -> AuthResponse:
    """This funciton is a wrapper function that implements the Rest authentication schema.

    It takes the credentials of the user and authenticates them on the authentication URL. After authenticating, it fetches the token and adds the token to the
    headers along with optional headers in case the user provided them.
    """

    auth_config = rest_config_parser(schema)
    return rest_auth_attach(user, auth_config)


def rest_reauthenticator(user: User, schema: dict, refresh_token: str) -> AuthResponse:
    """This funciton is a wrapper function that implements the Rest reauthentication schema.

    It takes the user information, the schema information and the refresh token and attempts reauthenticating the user using the refresh token
    """

    # Reparse the configuration
    auth_config = rest_config_parser(schema)

    # Now we will do the same thing we are doing in the authentication function
    # First we have to create a payload
    if auth_config['refresh_token_name'] is None or auth_config['refresh_url'] is None:
        raise AuthenticationError('Refresh Token found, please provide the refresh token name and the refresh URL')
    payload: dict = {auth_config['refresh_token_name']: refresh_token}

    # Now we have to send the payload
    response = requests.request(auth_config['method'], auth_config['refresh_url'], json=payload)

    # If there is a cookie that is fetched, added it to the auth response header
    cookie_header = response.cookies.get_dict()  # type: ignore[no-untyped-call]
    if cookie_header:
        cookie_header = [f'{name}={value}' for name, value in cookie_header.items()]
        cookie_header = ';'.join(cookie_header)
        if auth_config['cookie_auth'] and not cookie_header:
            raise AuthenticationError('Authentication Failed: No cookie was found')
    else:
        cookie_header = None

    # Prepare the header in order to fetch the token
    # We are creating a header for the token because the helper function '_extract_token' works like that
    headers: dict[str, str] = {}

    # Now we want to append the authentication headers
    # There are two parts
    # 1- If auth cookie is enabled, then we simply search add the cookie to the auth response and that is it
    # 2- If auth cookie is disables, we continue the authentication process
    if not auth_config['cookie_auth']:
        token_name = cast(str, auth_config['token_name'])
        if auth_config['header_name'] is None:
            headers['Authorization'] = ''
        else:
            headers[auth_config['header_name']] = ''

        if auth_config['header_key'] is not None:
            headers[next(iter(headers))] += auth_config['header_key'] + ' ' + '{{' + token_name + '}}'
        else:
            headers[next(iter(headers))] += 'Bearer {{' + token_name + '}}'

    # Append the optional headers to the header
    if auth_config['headers'] is not None:
        for name, value in auth_config['headers'].items():

            # Resolving duplicate keys
            if name in headers:
                headers[name] += ', ' + value

            else:
                headers[name] = value

    # Append the cookie header and check if the authentication type is a cookie authentication or no
    if cookie_header:
        headers['cookie'] = cookie_header
        if auth_config['cookie_auth']:
            return AuthResponse({
                'tech': AuthTech.REST,
                'headers': headers,
            })

    auth_response, refresh_token_result = extract_token(response, AuthTech.REST, headers, auth_config['refresh_token_name'])

    token = auth_response['headers'][next(iter(headers))].split(' ')[1]

    # Add the token and the expiry time to the user manager in order to be accessed by other parts of the program
    expiry_time: float | None = None
    try:
        expiry_time = jwt.decode(token, options={
            'verify_signature': False,
            'verify_exp': True,
        }).get('exp')
    except jwt.exceptions.DecodeError:
        pass
    finally:
        user.set_token(token, expiry_time)

    user.refresh_token = refresh_token_result

    return auth_response
