"""Implementation of the AWS authentication schema."""

import datetime
import hashlib
import hmac
from copy import deepcopy
from typing import Any, cast
from urllib.parse import urlparse

import boto3
import jwt
from pycognito.aws_srp import AWSSRP  # type: ignore[import]

from multiauth.helpers import get_secret_hash
from multiauth.manager import User
from multiauth.types.errors import AuthenticationError
from multiauth.types.http import HTTPMethod, Location
from multiauth.types.main import AuthAWSType, AuthResponse, AuthTech
from multiauth.types.providers.aws import AuthConfigAWS, AuthHashalgorithmHawkandAWS


def aws_check_type(user: User, schema: dict) -> AuthAWSType:
    """A function that returns the type of the AWS Authentication."""

    auth_config = aws_config_parser(user, schema)

    return auth_config['type']


def aws_config_parser(user: User, schema: dict) -> AuthConfigAWS:
    """This function parses the Digest schema and checks if all necessary fields exist."""

    auth_config = AuthConfigAWS({
        'type': AuthAWSType.USER_PASSWORD_AUTH,
        'region': '',
        'client_id': None,
        'method': None,
        'service_name': None,
        'hash_algorithm': None,
        'pool_id': None,
        'client_secret': None,
        'location': Location.HEADERS,
        'header_name': None,
        'header_key': None,
        'headers': None,
    })

    # Start by taking the type
    if not schema.get('type'):
        raise AuthenticationError('Please provide the type of AWS authentication that you want to perform')
    if not schema.get('region'):
        raise AuthenticationError('Please provide the region in which the service exists (eg: us-east-1)')
    if not schema.get('location'):
        raise AuthenticationError('Please provide with the location where the headers should be added')

    auth_config['type'] = schema['type']
    user.auth_type = schema['type']
    auth_config['region'] = schema['region']
    auth_config['location'] = Location(schema['location'])

    if auth_config['type'] == AuthAWSType.AWS_SIGNATURE:
        if not schema.get('service_name'):
            raise AuthenticationError('Please provide the service name in which you are trying to access (eg: EC2)')
        if not schema.get('method'):
            raise AuthenticationError('Please provide the method of the requests (usually POST)')
        if not schema.get('hash_algorithm'):
            raise AuthenticationError('Please provide the hashing algorithm')

        auth_config['service_name'] = schema['service_name']
        auth_config['method'] = schema['method']
        auth_config['hash_algorithm'] = AuthHashalgorithmHawkandAWS(schema['hash_algorithm'])

    else:
        if not schema.get('client_id'):
            raise AuthenticationError('Please provide the client ID')
        auth_config['client_id'] = schema['client_id']

        if auth_config['type'] == AuthAWSType.USER_SRP_AUTH:
            if not schema.get('pool_id'):
                raise AuthenticationError('Please provide the AWS cognito pool ID')
            auth_config['pool_id'] = schema['pool_id']

    # Options
    if 'options' in schema:
        auth_config['client_secret'] = schema['options'].get('client_secret')
        auth_config['header_name'] = schema['options'].get('header_name')
        auth_config['header_key'] = schema['options'].get('header_key')
        auth_config['headers'] = schema['options'].get('headers')

    return auth_config


def aws_user_password_handler(user: User, auth_config: AuthConfigAWS) -> dict:
    """This function is the handler for the USER_PASSWORD_AUTH authentication flow."""

    # First we have to fetch the user credentials from the user
    username, password = user.get_credentials()

    # Now we have to initiate the client
    client = boto3.client('cognito-idp', region_name=auth_config['region'])

    # Now we have to create the parameters
    parameters: dict[str, str] = {
        'USERNAME': username,
        'PASSWORD': password,
    }

    if auth_config['client_secret'] is not None:
        client_id = cast(str, auth_config['client_id'])
        parameters['SECRET_HASH'] = get_secret_hash(username, client_id, auth_config['client_secret'])

    # Now we have to initiate the connection
    response = client.initiate_auth(
        ClientId=auth_config['client_id'],
        AuthFlow=auth_config['type'].value,
        AuthParameters=parameters,
    )

    return response


def aws_user_srp_handler(user: User, auth_config: AuthConfigAWS) -> dict:
    """This function is the handler for the USER_SRP_AUTH authentication flow."""

    # First we have to fetch the user credentials from the user
    username, password = user.get_credentials()

    # Now we have to initiate the client
    client = boto3.client('cognito-idp', region_name=auth_config['region'])

    # Now we to make the connection and get the token
    connection = AWSSRP(
        username=username,
        password=password,
        pool_id=auth_config['pool_id'],
        client_id=auth_config['client_id'],
        client_secret=auth_config['client_secret'],
        client=client,
    )

    return connection.authenticate_user()


def aws_auth_attach(user: User, auth_config: AuthConfigAWS) -> AuthResponse:
    """This function attaches the user credentials to the schema and generates the proper authentication response."""

    aws_response: dict = {}
    headers: dict[str, str] = {}

    # First we need to check which authentication flow is used
    if auth_config['type'] == AuthAWSType.USER_PASSWORD_AUTH:
        aws_response = aws_user_password_handler(user, auth_config)
    elif auth_config['type'] == AuthAWSType.USER_SRP_AUTH:
        aws_response = aws_user_srp_handler(user, auth_config)
    elif auth_config['type'] == AuthAWSType.REFRESH_TOKEN:
        if not user.credentials:
            raise AuthenticationError('Configuration file error. Missing credentials')
        if not user.credentials.get('refresh_token'):
            raise AuthenticationError('Please provide the user with refresh token')
        refresh_token = user.credentials['refresh_token']
        return aws_reauthenticator(user, cast(dict, auth_config), refresh_token, parse=False)
    else:
        return AuthResponse({'tech': AuthTech.AWS, 'headers': {}})

    # Extract the access_token and the refresh token
    access_token: str = aws_response['AuthenticationResult']['AccessToken']
    refresh_token = aws_response['AuthenticationResult']['RefreshToken']

    # Now we to have prepare the header
    if auth_config['header_name'] is not None:
        headers[auth_config['header_name']] = ''
    else:
        headers['Authorization'] = ''

    if auth_config['header_key'] is not None:
        headers[next(iter(headers))] += auth_config['header_key'] + ' ' + access_token
    else:
        headers[next(iter(headers))] += 'Bearer ' + access_token

    # Append the optional headers to the header
    if auth_config['headers'] is not None:
        for name, value in auth_config['headers'].items():

            # Resolving duplicate keys
            if name in headers:
                headers[name] += ', ' + value
            else:
                headers[name] = value

    auth_response: AuthResponse = AuthResponse({
        'tech': AuthTech.AWS,
        'headers': headers,
    })

    # Add the token, the refresh token, and the expiry time to the user manager in order to be accessed by other parts of the program
    # First we have to check if the token is a JWT token (It should be)
    try:
        expiry_time = jwt.decode(access_token, options={
            'verify_signature': False,
            'verify_exp': True,
        }).get('exp')
    except Exception as e:
        raise AuthenticationError('The received token is not a JWT token') from e

    user.set_token(access_token, expiry_time)
    user.refresh_token = refresh_token

    return auth_response


def aws_authenticator(user: User, schema: dict) -> AuthResponse:
    """This function is a wrapper function that implements the AWS authentication schema.

    The AWS authentication is based on creating a signature based on the access key and the secret key to the API. After creating this signature, the signature
    is appended to a well crafted authentication header
    """

    auth_config = aws_config_parser(user, schema)
    return aws_auth_attach(user, auth_config)


def aws_reauthenticator(user: User, schema: dict, refresh_token: str, parse: bool = True) -> AuthResponse:
    """This function is a function that implements the AWS Authentication reauthentication.

    It takes schema and user as input, and it starts tth reauthentication process using the refreash token
    """

    # Reparse the configuration
    if parse:
        auth_config = aws_config_parser(user, schema)
    else:
        auth_config = cast(AuthConfigAWS, schema)

    # Now we have to initiate the reauth
    if auth_config['type'] == AuthAWSType.AWS_SIGNATURE:
        raise AuthenticationError('The AWS Signature is not handled here')

    client = boto3.client('cognito-idp', region_name=auth_config['region'])

    # Now we have to create the parameters
    parameters: dict[str, str] = {
        'REFRESH_TOKEN': refresh_token,
    }

    if auth_config['client_secret'] is not None:
        if user.credentials:
            if not user.credentials.get('username'):
                raise AuthenticationError('Please provide the username')

            username: str = user.credentials['username']

        client_id = cast(str, auth_config['client_id'])
        parameters['SECRET_HASH'] = get_secret_hash(username, client_id, auth_config['client_secret'])

    # Now we have to initiate the connection
    response = client.initiate_auth(
        ClientId=auth_config['client_id'],
        AuthFlow='REFRESH_TOKEN_AUTH',
        AuthParameters=parameters,
    )

    # Extract the access_token and the refresh token
    access_token: str = response['AuthenticationResult']['AccessToken']
    new_refresh_token: str = response['AuthenticationResult']['RefreshToken']

    try:
        expiry_time = jwt.decode(access_token, options={
            'verify_signature': False,
            'verify_exp': True,
        }).get('exp')
    except Exception as e:
        raise AuthenticationError('The received token is not a JWT token') from e

    user.set_token(access_token, expiry_time)
    user.refresh_token = new_refresh_token

    # Now we to have prepare the header
    headers: dict[str, str] = {}

    if not auth_config['header_name'] is not None:
        headers['Authorization'] = ''
    else:
        headers[auth_config['header_name']] = ''

    if auth_config['header_key'] is not None:
        headers[next(iter(headers))] += auth_config['header_key'] + ' ' + access_token
    else:
        headers[next(iter(headers))] += 'Bearer ' + access_token

    # Append the optional headers to the header
    if auth_config['headers'] is not None:
        for name, value in auth_config['headers'].items():

            # Resolving duplicate keys
            if name in headers:
                headers[name] += ', ' + value

            else:
                headers[name] = value

    auth_response: AuthResponse = AuthResponse({
        'tech': AuthTech.AWS,
        'headers': headers,
    })

    return auth_response


#pylint: disable=line-too-long, too-many-locals
def aws_signature(
    user: User,
    schema: dict,
    headers: dict[str, str],
    method: HTTPMethod,
    payload: Any,
    url: str,
) -> AuthResponse:
    """This function performs the AWS authentication by using the AWS signature v4."""

    auth_config = aws_config_parser(user, schema)

    # This is done according to https://docs.aws.amazon.com/code-samples/latest/catalog/python-signv4-v4-signing-get-post.py.html

    # First we take the user credentials
    if not user.credentials:
        raise AuthenticationError('Configuration file error. Missing credentials')
    if not user.credentials.get('AccessKey'):
        raise AuthenticationError('Please enter an access key')
    if not user.credentials.get('SecretKey'):
        raise AuthenticationError('Please enter a secret key')

    access_key = cast(str, user.credentials.get('AccessKey'))
    secret_key = cast(str, user.credentials.get('SecretKey'))

    # Now we have to create the signing funcitons
    def _sign(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _get_signature_key(key: str, date_stamp: str, region_name: str, service_name: str) -> bytes:
        key_date = _sign(('AWS4' + key).encode('utf-8'), date_stamp)
        key_region = _sign(key_date, region_name)
        key_service = _sign(key_region, service_name)
        key_signing = _sign(key_service, 'aws4_request')
        return key_signing

    # Now we have to define a couple of variables that will help us in the signing
    time = datetime.datetime.utcnow()
    amz_date = time.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = time.strftime('%Y%m%d')

    # Now we have to analyze the URL
    parsed_url = urlparse(url)

    # We want the host
    host = parsed_url.netloc

    # We also want the path
    path = parsed_url.path

    # Add optional header
    _headers: dict[str, str] = deepcopy(headers)
    if auth_config['headers'] is not None:
        for name, value in auth_config['headers'].items():
            # Resolving duplicate keys
            if name in _headers and value not in _headers[name]:
                _headers[name] += ', ' + value
            else:
                _headers[name] = value

    # Now we have to prepare the headers
    signed_header = 'host;x-amz-date'
    canonical_header = 'host: ' + host + '\n' + 'x-amz-date: ' + amz_date
    for header_name, header_value in _headers.items():
        canonical_header += header_name + ': ' + header_value + '\n'
        signed_header += header_name + ';'

    canonical_header = canonical_header[:-1]
    signed_header = signed_header[:-1]

    # Now we have to hash the payload
    payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

    # Now we have to create the cannonical URL
    if method == 'POST':
        canonical_request = method + '\n' + path + '\n' + '\n' + canonical_header + '\n' + signed_header + '\n' + payload_hash + '\n'
    else:
        canonical_request = method + '\n' + path + '\n' + payload + '\n' + canonical_header + '\n' + signed_header + '\n' + '\n'

    # Now we have to create the strings to sign
    algorithm = 'AWS4-HMAC-SHA256'
    region: str = auth_config['region']
    service: str = cast(str, auth_config['service_name'])
    credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' + amz_date + '\n' + credential_scope + '\n' + hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

    # Calculate the signature
    signing_key = _get_signature_key(secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

    # Creating the header
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_header + ', ' + 'Signature=' + signature

    # Add header
    _headers['Authorization'] = authorization_header

    return AuthResponse({
        'tech': AuthTech.AWS,
        'headers': _headers,
    })
