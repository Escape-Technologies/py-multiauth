"""Implementation of the OAuth authentication schema."""

import time
from typing import cast

from authlib.integrations.requests_client import OAuth2Session  # type: ignore[import]

from multiauth.helpers import authentication_portal, token_endpoint_auth_method
from multiauth.manager import User
from multiauth.types.errors import AuthenticationError
from multiauth.types.http import Location
from multiauth.types.main import AuthResponse, AuthTech
from multiauth.types.providers.oauth import AuthConfigOAuth, AuthOAuthGrantType, AuthOAuthlocation, AuthOAuthResponse


def extract_oauth_token(user: User, auth_config: AuthConfigOAuth, oauth_response: dict) -> AuthResponse:
    """Extract the token, refresh token, and the expiry time from the OAuth access token response."""

    # Initialize the variables
    auth_response = AuthResponse({
        'headers': {},
        'tech': AuthTech.OAUTH,
    })

    response = AuthOAuthResponse({
        'access_token': '',
        'expires_in': None,
        'refresh_token': None,
    })

    if not oauth_response or not isinstance(oauth_response, dict):
        raise AuthenticationError('Invalid OAuth Response')
    if not oauth_response.get('access_token'):
        raise AuthenticationError('Invalid OAuth Response')

    response['access_token'] = oauth_response['access_token']
    response['refresh_token'] = oauth_response.get('refresh_token')

    # The expire_at field is the amount of seconds to expire. So we need to calculate the UNIX expiry date
    if oauth_response.get('expires_at'):
        response['expires_in'] = int(oauth_response['expires_at']) + time.time()

    # Now check the location to know where should add the token (header or body)
    if auth_config['location'] == Location.HEADERS:
        auth_response['headers']['authorization'] = auth_config['header_prefix'] + ' ' + response['access_token']

    elif auth_config['location'] == Location.URL:
        pass

    # Add the token, the refresh token, and the expiry time to the user manager in order to be accessed by other parts of the program
    user.set_token(response['access_token'], response['expires_in'])
    user.refresh_token = response['refresh_token']

    # Append the optional headers to the header
    if auth_config['headers'] is not None:
        for name, value in auth_config['headers'].items():

            # Resolving duplicate keys
            if name in auth_response['headers']:
                auth_response['headers'][name] += ', ' + value
            else:
                auth_response['headers'][name] = value

    return auth_response


def auth_code_session(user: User, auth_config: AuthConfigOAuth) -> OAuth2Session:
    """Creates the authentication code seesion."""

    # First we have to fetch the user credentials from the user
    if not user.credentials:
        raise AuthenticationError('Configuration file error. Missing credentials')
    if not user.credentials.get('client_id'):
        raise AuthenticationError('Please provide the user with client ID')
    if not user.credentials.get('client_secret'):
        raise AuthenticationError('Please provide the user with client secret')

    client_id: str = user.credentials['client_id']
    client_secret: str = user.credentials['client_secret']

    # Create an OAuth session using the Authlib library functions
    client = OAuth2Session(
        client_id,
        client_secret,
        token_endpoint_auth_method=token_endpoint_auth_method(auth_config['auth_location']),
        scope=auth_config['scope'],
    )

    return client


def auth_code_handler(user: User, auth_config: AuthConfigOAuth) -> dict:
    """Handles the authentication code OAuth type."""

    # First initiate the OAuth Session
    client = auth_code_session(user, auth_config)

    # Now after we create the client, we have to create the authentication url
    authentication_url, _ = client.create_authorization_url(
        auth_config['authentication_endpoint'], state=auth_config['state'], code_verifier=auth_config['code_verifier']
    )

    # Now we have to pass the authorization URL and the callback URL to the browser in order to fetch the what is necessary
    # The if condition is to simply avoid mypy errors
    if auth_config['callback_url'] is not None:
        exit_code, authorization_response = authentication_portal(authentication_url, auth_config['callback_url'])
        if exit_code == 0:
            raise AuthenticationError('Authentication Error. Please complete the authentication')

    # Now finally, we have to fetch the access token in order to use it for the applicaiton
    return client.fetch_token(auth_config['token_endpoint'], authorization_response=authorization_response)


def implicit_session(user: User, auth_config: AuthConfigOAuth) -> OAuth2Session:
    """Creates the session for implicit authentication."""

    # First as usual we have to fetch the credentials from the user
    if not user.credentials:
        raise AuthenticationError('Configuration file error. Missing credentials')
    if not user.credentials.get('client_id'):
        raise AuthenticationError('Please provide the user with client ID')

    client_id: str = user.credentials['client_id']

    # Create an OAuth session using the Authlib library functions
    client = OAuth2Session(
        client_id,
        token_endpoint_auth_method=token_endpoint_auth_method(auth_config['auth_location']),
        scope=auth_config['scope'],
    )

    return client


def implicit_handler(user: User, auth_config: AuthConfigOAuth) -> dict:
    """Handles the implicit authentication OAuth type."""

    # First initiate the OAuth session
    client = implicit_session(user, auth_config)

    authentication_url, _ = client.create_authorization_url(auth_config['authentication_endpoint'], state=auth_config['state'])

    # Now we have to pass the authorization URL and the callback URL to the browser in order to fetch the what is necessary
    # The if condition is to simply avoid mypy errors
    if auth_config['callback_url'] is not None:
        exit_code, authorization_response = authentication_portal(authentication_url, auth_config['callback_url'])
        if exit_code == 0:
            raise AuthenticationError('Authentication Error. Please complete the authentication')

    return client.fetch_token(authorization_response=authorization_response)


def client_cred_session(user: User, auth_config: AuthConfigOAuth) -> OAuth2Session:
    """Creates the session for client credentials authentication."""

    # First we have to fetch the user credentials from the user
    if not user.credentials:
        raise AuthenticationError('Configuration file error. Missing credentials')
    if not user.credentials.get('client_id'):
        raise AuthenticationError('Please provide the user with client ID')
    if not user.credentials.get('client_secret'):
        raise AuthenticationError('Please provide the user with client secret')

    client_id: str = user.credentials['client_id']
    client_secret: str = user.credentials['client_secret']

    # Create an OAuth session using the Authlib library functions
    client = OAuth2Session(
        client_id,
        client_secret,
        token_endpoint_auth_method=token_endpoint_auth_method(auth_config['auth_location']),
        scope=auth_config['scope'],
    )

    return client


def client_cred_handler(user: User, auth_config: AuthConfigOAuth) -> dict:
    """Handles the client credentials authentication OAuth type."""

    # First initiate the OAuth session
    client = client_cred_session(user, auth_config)

    return client.fetch_token(auth_config['token_endpoint'])


def password_cred_session(user: User, auth_config: AuthConfigOAuth) -> tuple[OAuth2Session, str, str]:
    """Creates the session for password credentials authentication."""

    # First we have to fetch the user credentials from the user
    if not user.credentials:
        raise AuthenticationError('Configuration file error. Missing credentials')
    if not user.credentials.get('client_id'):
        raise AuthenticationError('Please provide the user with client ID')
    if not user.credentials.get('client_secret'):
        raise AuthenticationError('Please provide the user with client secret')
    if not user.credentials.get('username'):
        raise AuthenticationError('Please provide the user with username')
    if not user.credentials.get('password'):
        raise AuthenticationError('Please provide the user with password')

    client_id: str = user.credentials['client_id']
    client_secret: str = user.credentials['client_secret']
    client_username: str = user.credentials['username']
    client_password: str = user.credentials['password']

    # Create an OAuth session using the Authlib library functions
    client = OAuth2Session(
        client_id,
        client_secret,
        token_endpoint_auth_method=token_endpoint_auth_method(auth_config['auth_location']),
        scope=auth_config['scope'],
    )

    return client, client_username, client_password


def password_cred_handler(user: User, auth_config: AuthConfigOAuth) -> dict:
    """Handles the client credentials authentication OAuth type."""

    client, client_username, client_password = password_cred_session(user, auth_config)

    return client.fetch_token(auth_config['token_endpoint'], username=client_username, password=client_password)


def oauth_config_parser(schema: dict) -> AuthConfigOAuth:
    """This function parses the OAuth schema and checks if all necessary fields exist."""

    auth_config: AuthConfigOAuth = AuthConfigOAuth({
        'grant_type': AuthOAuthGrantType.AUTH_CODE,
        'authentication_endpoint': None,
        'token_endpoint': None,
        'callback_url': None,
        'scope': '',
        'header_prefix': '',
        'auth_location': AuthOAuthlocation.BODY,
        'location': Location.HEADERS,
        'state': None,
        # 'challenge_method': None,
        'code_verifier': None,
        'headers': None,
    })

    if not schema.get('grant_type'):
        raise AuthenticationError('Please provide the grant type')
    auth_config['grant_type'] = AuthOAuthGrantType(schema.get('grant_type'))
    # USER_MANAGER.set_current_user_auth_type(schema.get('grant_type'))

    # Now according to the grant type we will have to check the parser
    if auth_config['grant_type'] in (AuthOAuthGrantType.AUTH_CODE, AuthOAuthGrantType.IMPLICIT):
        if not schema.get('authentication_endpoint'):
            raise AuthenticationError('Please provide an authentication endpoint')
        auth_config['authentication_endpoint'] = schema.get('authentication_endpoint')

    if auth_config['grant_type'] != AuthOAuthGrantType.IMPLICIT:
        if not schema.get('token_endpoint'):
            raise AuthenticationError('Please provide an token endpoint')
        auth_config['token_endpoint'] = schema.get('token_endpoint')

    if auth_config['grant_type'] in (AuthOAuthGrantType.AUTH_CODE, AuthOAuthGrantType.IMPLICIT):
        if not schema.get('callback_url'):
            raise AuthenticationError('Please provide the authenticaiton endpoint')
        auth_config['callback_url'] = schema.get('callback_url')

    if not schema.get('scope'):
        raise AuthenticationError('Please provide the scope for the authentication')
    auth_config['scope'] = schema['scope']

    if not schema.get('header_prefix'):
        raise AuthenticationError('Please provide the header prefix')
    auth_config['header_prefix'] = schema['header_prefix']

    if not schema.get('auth_location'):
        raise AuthenticationError('Please provide the authentication location')
    auth_config['auth_location'] = AuthOAuthlocation(schema.get('auth_location'))

    if not schema.get('location'):
        raise AuthenticationError('Please provide the location')
    auth_config['location'] = Location(schema.get('location'))

    # Options
    if 'options' in schema:
        auth_config['state'] = schema['options'].get('state')
        auth_config['code_verifier'] = schema['options'].get('code_verifier')
        auth_config['headers'] = schema['options'].get('headers')

    return auth_config


def oauth_auth_attach(user: User, auth_config: AuthConfigOAuth) -> AuthResponse:
    """This function attaches the user credentials to the schema and generates the proper authentication response according to the grant type."""

    # First according every grant type, we will create a handler
    grant_type: AuthOAuthGrantType = auth_config['grant_type']
    oauth_response: dict = {}

    if grant_type == AuthOAuthGrantType.AUTH_CODE:
        oauth_response = auth_code_handler(user, auth_config)

    elif grant_type == AuthOAuthGrantType.IMPLICIT:
        oauth_response = implicit_handler(user, auth_config)

    elif grant_type == AuthOAuthGrantType.CLIENT_CRED:
        oauth_response = client_cred_handler(user, auth_config)

    elif grant_type == AuthOAuthGrantType.PASSWORD_CRED:
        oauth_response = password_cred_handler(user, auth_config)

    elif grant_type == AuthOAuthGrantType.REFRESH_TOKEN:
        if not user.credentials:
            raise AuthenticationError('Configuration file error. Missing credentials')
        if not user.credentials.get('refresh_token'):
            raise AuthenticationError('Please provide the user with refresh token')
        refresh_token = user.credentials['refresh_token']
        return oauth_reauthenticator(user, cast(dict, auth_config), refresh_token, parse=False)

    return extract_oauth_token(user, auth_config, oauth_response)


def oauth_authenticator(user: User, schema: dict) -> AuthResponse:
    """This function is a wrapper function that implements the OAuth authentication schema.

    It starts by identifying the grant type and then use the appropriate grant type funtion in order to authenticate the user to the application.
    """

    auth_config = oauth_config_parser(schema)
    return oauth_auth_attach(user, auth_config)


def oauth_reauthenticator(user: User, schema: dict, refresh_token: str, parse: bool = True) -> AuthResponse:
    """This function is a function that implements the OAuth reauthentication.

    It takes the schema and user, and it starts the reauthentication process using the refresh token.
    """

    # Reparse the configuration
    if parse:
        auth_config = oauth_config_parser(schema)
    else:
        auth_config = cast(AuthConfigOAuth, schema)

    # Since authentication requires the existance of an authentication token, Only check the grant type that require an authentication token endpoint as input

    if auth_config['grant_type'] in (AuthOAuthGrantType.AUTH_CODE, AuthOAuthGrantType.REFRESH_TOKEN):
        client = auth_code_session(user, auth_config)

    elif auth_config['grant_type'] == AuthOAuthGrantType.CLIENT_CRED:
        client = client_cred_session(user, auth_config)

    elif auth_config['grant_type'] == AuthOAuthGrantType.PASSWORD_CRED:
        client, _, _ = password_cred_session(user, auth_config)

    elif auth_config['grant_type'] == AuthOAuthGrantType.IMPLICIT:
        client = implicit_session(user, auth_config)

    if auth_config['token_endpoint']:
        new_token = client.refresh_token(auth_config['token_endpoint'], refresh_token)

        return extract_oauth_token(user, auth_config, new_token)

    if auth_config['grant_type'] == AuthOAuthGrantType.REFRESH_TOKEN and not auth_config['token_endpoint']:
        raise AuthenticationError('Please provide the token endpoint')

    return oauth_auth_attach(user, auth_config)
