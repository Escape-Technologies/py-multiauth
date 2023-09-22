"""Implementation of the Digest authentication schema."""

import hashlib
import os
import time
from typing import Dict, Optional
from urllib.parse import urlparse

import requests

from multiauth.entities.errors import AuthenticationError
from multiauth.entities.http import HTTPMethod
from multiauth.entities.main import (
    AuthConfigDigest,
    AuthDigestChallenge,
    AuthHashAlgorithmDigest,
    AuthResponse,
    AuthTech,
)
from multiauth.helpers import hash_calculator
from multiauth.manager import User

# from escape_cli.common.user import USER_MANAGER


def send_401_request(url: str) -> AuthDigestChallenge:
    """Sending a 401 request and parsing it according to RFC 2617."""

    challenge = AuthDigestChallenge(
        {
            'realm': None,
            'domain': None,
            'nonce': None,
            'opaque': None,
            'algorithm': None,
            'qop_options': None,
        },
    )

    # Send an empty get request to get the parameters necessary for the authentication
    response = requests.get(url, timeout=5)

    # We need to parse the response
    if response.headers.get('WWW-Authenticate'):
        parameters_list = response.headers['WWW-Authenticate'].replace(', ', ' ').split(' ')[1::]

        parameters = {}
        for parameter in parameters_list:
            temp = parameter.split('=')
            parameters[temp[0]] = temp[1].replace('"', '')

        challenge['realm'] = parameters.get('realm')

        if parameters.get('domain'):
            challenge['domain'] = parameters.get('domain')

        else:
            parsed_url = urlparse(url)
            challenge['domain'] = parsed_url.path or '/'
            if parsed_url.query and challenge['domain'] is not None:
                challenge['domain'] += '?' + parsed_url.query

        challenge['nonce'] = parameters.get('nonce')
        challenge['opaque'] = parameters.get('opaque')

        if parameters.get('algorithm'):
            challenge['algorithm'] = AuthHashAlgorithmDigest(parameters.get('algorithm'))
        else:
            challenge['algorithm'] = AuthHashAlgorithmDigest.MD5

        challenge['qop_options'] = parameters.get('qop')

    return challenge


# pylint: disable=[too-many-branches, too-many-statements]
def digest_config_parser(schema: Dict) -> AuthConfigDigest:
    """This function parses the Digest schema and checks if all necessary fields exist."""

    auth_config = AuthConfigDigest(
        {
            'url': '',
            'realm': '',
            'nonce': '',
            'algorithm': AuthHashAlgorithmDigest.MD5,
            'domain': '',
            'method': 'POST',
            'qop': None,
            'nonce_count': None,
            'client_nonce': None,
            'opaque': None,
            'headers': None,
        },
    )

    if not schema.get('url'):
        raise AuthenticationError('Please provide a URL to the web application')
    auth_config['url'] = schema['url']

    # Now send a 401 Request to get the needed parameters
    parameters = send_401_request(auth_config['url'])

    # Now fill the optional parameters
    # Hopefully this parsing is compatible with RFC 2617
    # Note all of these are just operations found in RFC 2617

    if schema['options'].get('realm'):
        auth_config['realm'] = schema['options'].get('realm')
    else:
        if parameters['realm'] is None:
            raise AuthenticationError(
                'Cannot retrieve the value of the realm from the server. Please provide the realm value',
            )
        auth_config['realm'] = parameters['realm']

    if schema['options'].get('nonce'):
        auth_config['nonce'] = schema['options'].get('nonce')
    else:
        if parameters['nonce'] is None:
            raise AuthenticationError(
                'Cannot retrieve the value of the nonce from the server. Please provide the value of the nonce',
            )
        auth_config['nonce'] = parameters['nonce']

    if schema['options'].get('algorithm'):
        auth_config['algorithm'] = AuthHashAlgorithmDigest(schema['options'].get('algorithm'))
    else:
        if parameters['algorithm'] is None:
            raise AuthenticationError('No value for parameters algorithm')
        auth_config['algorithm'] = parameters['algorithm']

    if not schema['options'].get('method'):
        raise AuthenticationError('Please provide the used method in the API')

    auth_config['method'] = schema['options'].get('method')

    auth_config['qop'] = schema['options'].get('qop')
    if not auth_config['qop']:
        auth_config['qop'] = parameters['qop_options']

    auth_config['opaque'] = schema['options'].get('opaque')
    if not auth_config['opaque']:
        auth_config['opaque'] = parameters['opaque']

    auth_config['nonce_count'] = schema['options'].get('nonce_count')
    if not auth_config['nonce_count']:
        if auth_config['qop'] is not None and (auth_config['qop'] == 'auth' or 'auth' in auth_config['qop'].split(',')):
            nonce_count = 1
            auth_config['nonce_count'] = f'{nonce_count:08x}'

    auth_config['client_nonce'] = schema['options'].get('client_nonce')
    if not auth_config['client_nonce']:
        if auth_config['qop'] is not None and (auth_config['qop'] == 'auth' or 'auth' in auth_config['qop'].split(',')):
            # Taken from the request library for auth
            s = str(auth_config['nonce_count']).encode('utf-8')
            s += auth_config['nonce'].encode('utf-8')
            s += time.ctime().encode('utf-8')
            s += os.urandom(8)

            auth_config['client_nonce'] = hashlib.sha1(s).hexdigest()[:16]

    if parameters['domain'] is not None:
        auth_config['domain'] = parameters['domain']
    else:
        raise AuthenticationError('No value for parameters domain')

    auth_config['headers'] = schema['options'].get('headers')

    return auth_config


def digest_auth_attach(
    user: User,
    auth_config: AuthConfigDigest,
    method: Optional[HTTPMethod],
) -> AuthResponse:
    """This function attaches the user credentials to the schema and generates the proper authentication response."""

    auth_response = AuthResponse(
        {
            'headers': {},
            'tech': AuthTech.DIGEST,
        },
    )

    # Response Calculator
    def kd(secret: str, data: str) -> str:
        return hash_calculator(auth_config['algorithm'], f'{secret}:{data}')

    # First take user credentials
    username, password = user.get_credentials_pair()

    # Now we have to start calculating the response to the challenge
    a1 = f'{username}:{auth_config["realm"]}:{password}'
    if method:
        a2 = f'{method}:{auth_config["domain"]}'
    else:
        a2 = f'{auth_config["method"]}:{auth_config["domain"]}'

    ha1 = hash_calculator(auth_config['algorithm'], a1)
    ha2 = hash_calculator(auth_config['algorithm'], a2)

    if (
        auth_config['algorithm'] == AuthHashAlgorithmDigest.MD5_SESS
        or auth_config['algorithm'] == AuthHashAlgorithmDigest.SHA_256_SESS
        or auth_config['algorithm'] == AuthHashAlgorithmDigest.SHA_512_256_SESS
    ):
        ha1 = hash_calculator(auth_config['algorithm'], f'{ha1}:{auth_config["nonce"]}:{auth_config["client_nonce"]}')

    response = ''

    if auth_config['qop'] is not None and (auth_config['qop'] == 'auth' or 'auth' in auth_config['qop'].split(',')):
        temp = f'{auth_config["nonce"]}:{auth_config["nonce_count"]}:{auth_config["client_nonce"]}:auth:{ha2}'
        response = kd(ha1, temp)

    else:
        response = kd(ha1, f'{auth_config["nonce"]}:{ha2}')

    header_value = f'username="{username}", realm="{auth_config["realm"]}", nonce="{auth_config["nonce"]}", uri="{auth_config["domain"]}"'
    header_value += f', response="{response}"'

    if auth_config['opaque']:
        header_value += f', opaque="{auth_config["opaque"]}"'
    if auth_config['algorithm']:
        header_value += f', algorithm="{auth_config["algorithm"].value.upper()}"'
    if auth_config['qop']:
        header_value += f', qop="auth", nc="{auth_config["nonce_count"]}", cnonce="{auth_config["client_nonce"]}"'

    # Add token to the current user
    user.set_token(header_value, None)

    header = {}
    header['Authorization'] = f'Digest {header_value}'

    # Append the optional headers to the header
    if auth_config['headers'] is not None:
        for name, value in auth_config['headers'].items():
            # Resolving duplicate keys
            if name in header:
                header[name] += ', ' + value

            else:
                header[name] = value

    auth_response['headers'] = header

    return auth_response


def digest_authenticator(
    user: User,
    schema: Dict,
    method: Optional[HTTPMethod],
) -> AuthResponse:
    """This function is a wrapper function that implements the Digest authentication schema.

    It starts by sending an empty get request which allows it to fetch the configuration for the digest from the server using the WWW-Authenticate. After that,
    it sends the credentials using the options provided from the server.
    """

    auth_config = digest_config_parser(schema)
    return digest_auth_attach(user, auth_config, method)
