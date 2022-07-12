"""Implementation of the GraphQL authentication schema."""

import re
from typing import Any, Match, cast

import jwt
import requests

from multiauth.helpers import extract_token
from multiauth.manager import User
from multiauth.types.errors import AuthenticationError
from multiauth.types.main import AuthResponse, AuthTech
from multiauth.types.providers.graphql import AuthConfigGraphQl

# from escape_cli.common.user import USER_MANAGER


def format_arguments(credentials: dict) -> str:
    """Generates the arguments for the graphql authentication schema."""

    arguments: str = ''

    for cred_field, cred_value in credentials.items():
        if isinstance(cred_value, dict):
            arguments += cred_field + ': {' + format_arguments(cred_value) + '},'

        else:
            arguments += cred_field + ': \"' + cred_value + '\",'

    return arguments[:-1]


def generate_authentication_mutation(
    user: User,
    auth_config: AuthConfigGraphQl,
    credentials: dict[str, Any] | None = None,
    refresh: bool = False,
    refresh_field: bool = True,
) -> dict:
    """Generate the graphQL query."""

    # Take the credentials from the users
    if credentials is None:
        credentials = user.credentials
        if not credentials:
            raise AuthenticationError('Configuration file error. Missing credentials')

    try:
        # This variable will host the login information part of the mutation example: (login: admin@ecape.tech, password: "p@ssword123")
        arguments: str = '(' + format_arguments(credentials) + ')'

        # Here we start forming the Mutation string
        # Here we have to take the case if refresh is true
        if refresh:
            if auth_config['refresh_mutation_name'] is None:
                raise AuthenticationError('Configuration file error. Missing refresh_mutation_name')

            if refresh_field and auth_config['refresh_mutation_name'] is not None:
                graphql_query = 'mutation {' + auth_config['refresh_mutation_name'] + arguments + '{ \n'
            else:
                if auth_config['refresh_mutation_name'] is not None:
                    graphql_query = 'mutation {' + auth_config['refresh_mutation_name'] + arguments + '\n'
        else:
            graphql_query = 'mutation {' + auth_config['mutation_name'] + arguments + '{ \n'
        graphql_query += auth_config['mutation_field'] + '\n'
        if auth_config['refresh_field_name'] is not None:
            graphql_query += auth_config['refresh_field_name'] + '\n'
        if auth_config['headers'] is not None:
            for header_arg in auth_config['headers'].values():
                if '{{' in header_arg and '}}' in header_arg:
                    graphql_query += cast(Match, re.search('{{(.*)}}', header_arg)).group(1) + '\n'

        if refresh_field:
            graphql_query = graphql_query[:-1] + '}}'
        else:
            graphql_query = graphql_query[:-1] + '}'

        return {
            'http_method': auth_config['method'],
            'graphql_query': graphql_query,
            'graphql_variables': None,
        }

    except KeyError as error:
        raise KeyError(f'The key {error} is missing in the graphql auth config') from error


def graphql_config_parser(schema: dict) -> AuthConfigGraphQl:
    """This function parses the GraphQL schema and checks if all necessary fields exist."""

    auth_config = AuthConfigGraphQl({
        'url': '',
        'mutation_name': 'str',
        'method': 'POST',
        'cookie_auth': False,
        'mutation_field': '',
        'operation': 'mutation',
        'refresh_mutation_name': None,
        'refresh_field_name': None,
        'refresh_field': True,
        'header_name': None,
        'header_key': None,
        'headers': None,
    })

    if not schema.get('url'):
        raise AuthenticationError('Please provide with the authentication URL')
    if not schema.get('mutation_name'):
        raise AuthenticationError('Please provide the mutation name for the authentication')
    if not schema.get('mutation_field'):
        raise AuthenticationError('Please provide the mutation field in the authentication response')
    if not schema.get('method'):
        raise AuthenticationError('Please the HTTP method used for the authentication process')

    auth_config['url'] = schema['url']
    auth_config['mutation_name'] = schema['mutation_name']
    auth_config['mutation_field'] = schema['mutation_field']
    auth_config['method'] = schema['method']

    # Options
    if 'options' in schema:
        auth_config['refresh_mutation_name'] = schema['options'].get('refresh_mutation_name')
        auth_config['refresh_field_name'] = schema['options'].get('refresh_field_name')
        auth_config['refresh_field'] = schema['options'].get('refresh_field', True)
        auth_config['operation'] = schema['options'].get('operation', 'mutation')
        auth_config['cookie_auth'] = schema['options'].get('cookie_auth', False)
        auth_config['header_name'] = schema['options'].get('header_name')
        auth_config['header_key'] = schema['options'].get('header_key')
        auth_config['headers'] = schema['options'].get('headers')

    return auth_config


#pylint: disable=too-many-branches
def graphql_auth_attach(user: User, auth_config: AuthConfigGraphQl) -> AuthResponse:
    """This function attaches the user credentials to the schema and generates the proper authentication response."""

    # First we have to generate the graphQL query that we need to send
    graphql_query = generate_authentication_mutation(user, auth_config)
    data: dict[Any, Any]

    # Create the payload
    if not graphql_query['graphql_variables']:
        data = {'query': graphql_query['graphql_query']}

    else:
        data = {'query': graphql_query['graphql_query'], 'variables': graphql_query['graphql_variables']}

    print(data)
    # Now we need to send the request
    response = requests.request(auth_config['method'], auth_config['url'], json=data)

    # If there is a cookie that is fetched, added it to the auth response header
    cookie_header = response.cookies.get_dict()  # type: ignore[no-untyped-call]
    if cookie_header:
        cookie_header = [f'{name}={value}' for name, value in cookie_header.items()]
        cookie_header = ';'.join(cookie_header)
    else:
        if auth_config['cookie_auth']:
            raise AuthenticationError('No cookie found in the response')

        cookie_header = None

    # Prepare the header in order to fetch the token
    # We are creating a header for the token because the helper function '_extract_token' works like that
    headers: dict[str, str] = {}

    # Now we want to append the authentication headers
    # There are two parts
    # 1- If auth cookie is enabled, then we simply search add the cookie to the auth response and that is it
    # 2- If auth cookie is disables, we continue the authentication process
    if not auth_config['cookie_auth']:
        if auth_config['header_name'] is None:
            headers['Authorization'] = ''
        else:
            headers[auth_config['header_name']] = ''

        if auth_config['header_key'] is not None:
            headers[next(iter(headers))] += auth_config['header_key'] + ' ' + '{{' + auth_config['mutation_field'] + '}}'
        else:
            headers[next(iter(headers))] += 'Bearer {{' + auth_config['mutation_field'] + '}}'

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
                'tech': AuthTech.GRAPHQL,
                'headers': headers,
            })

    # Now fetch the token and create the Authentication Response
    auth_response, refresh_token = extract_token(response, AuthTech.REST, headers, auth_config['refresh_field_name'])

    token = auth_response['headers'][next(iter(headers))].split(' ')[1]

    # If the token is not a JWT token, don't add expiry time (No way of knowing if the token is expired or no)
    try:
        expiry_time = jwt.decode(token, options={
            'verify_signature': False,
            'verify_exp': True,
        }).get('exp')
    except Exception:
        return auth_response

    # Add the token and the expiry time to the user manager in order to be accessed by other parts of the program
    user.set_token(token, expiry_time)

    user.refresh_token = refresh_token

    return auth_response


def graphql_authenticator(user: User, schema: dict) -> AuthResponse:
    """This function is a wrapper function that implements the GraphQL authentication schema.

    It sends a mutation having the credentials of the user as the arguments to the mutations. Once it receives the response, it fetches the tokens and creates
    the authentication response
    """

    auth_config = graphql_config_parser(schema)
    return graphql_auth_attach(user, auth_config)


def graphql_reauthenticator(user: User, schema: dict, refresh_token: str) -> AuthResponse:
    """This function is a wrapper function that implements the GraphQL reauthentication schema.

    It takes the user information, the schema information, and the refresh token and attempts to reauthenticate by sending the refresh token to a muatation and
    receiving back an access token and a refresh token.
    """

    # Reparse the configuration
    auth_config = graphql_config_parser(schema)

    # Now we have to generate the graphQL query that we need to send
    # To do that we have to generate a dictionary
    credentials: dict = {auth_config['refresh_field_name']: refresh_token}

    # Now we do the same thing we do in the function above
    # First we have to generate the graphQL query that we need to send
    graphql_query = generate_authentication_mutation(user, auth_config, credentials, refresh=True, refresh_field=auth_config['refresh_field'])
    data: dict[Any, Any]

    # Create the payload
    if not graphql_query['graphql_variables']:
        data = {'query': graphql_query['graphql_query']}

    else:
        data = {'query': graphql_query['graphql_query'], 'variables': graphql_query['graphql_variables']}

    # Now we need to send the request
    response = requests.request(auth_config['method'], auth_config['url'], json=data)

    # If there is a cookie that is fetched, added it to the auth response header
    cookie_header = response.cookies.get_dict()  # type: ignore[no-untyped-call]
    if cookie_header:
        cookie_header = [f'{name}={value}' for name, value in cookie_header.items()]
        cookie_header = ';'.join(cookie_header)
    else:
        if auth_config['cookie_auth']:
            raise AuthenticationError('No cookie found in the response')

        cookie_header = None

    # Prepare the header in order to fetch the token
    # We are creating a header for the token because the helper function '_extract_token' works like that
    headers: dict[str, str] = {}

    # Now we want to append the authentication headers
    # There are two parts
    # 1- If auth cookie is enabled, then we simply search add the cookie to the auth response and that is it
    # 2- If auth cookie is disables, we continue the authentication process
    if not auth_config['cookie_auth']:
        if auth_config['header_name'] is None:
            headers['Authorization'] = ''
        else:
            headers[auth_config['header_name']] = ''

        if auth_config['header_key'] is not None:
            headers[next(iter(headers))] += auth_config['header_key'] + ' ' + '{{' + auth_config['mutation_field'] + '}}'
        else:
            headers[next(iter(headers))] += 'Bearer {{' + auth_config['mutation_field'] + '}}'

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
                'tech': AuthTech.GRAPHQL,
                'headers': headers,
            })

    # Now fetch the token and create the Authentication Response
    auth_response, refresh_token_result = extract_token(response, AuthTech.REST, headers, auth_config['refresh_field_name'])

    token = auth_response['headers'][next(iter(headers))].split(' ')[1]

    # If the token is not a JWT token, don't add expiry time (No way of knowing if the token is expired or no)
    try:
        expiry_time = jwt.decode(token, options={
            'verify_signature': False,
            'verify_exp': True,
        }).get('exp')
    except Exception:
        return auth_response

    # Add the token and the expiry time to the user manager in order to be accessed by other parts of the program
    user.set_token(token, expiry_time)

    user.refresh_token = refresh_token_result

    return auth_response
