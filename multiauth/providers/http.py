"""Implementation of the Rest authentication schema."""

from enum import Enum
from http import HTTPMethod
from typing import Dict, Type
from urllib.parse import urlparse

from multiauth.entities.errors import AuthenticationError
from multiauth.entities.main import AuthResponse, AuthTech
from multiauth.entities.providers.http import (
    AuthExtractor,
    AuthInjector,
    AuthProvider,
    AuthRequester,
    HTTPLocation,
)
from multiauth.manager import User

# from escape_cli.common.user import USER_MANAGER


def is_url(url: str) -> bool:
    """This function checks if the url is valid."""

    parsed_url = urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)


def in_enum(method: str, myenum: Type[Enum]) -> bool:
    """This function checks if the http method is valid."""

    try:
        myenum(method.upper())
        return True
    except ValueError:
        return False


def _parser_requester(schema: dict) -> AuthRequester:
    """This function parses the input schema and checks if all the necessary fields exist."""

    if 'url' not in schema:
        raise AuthenticationError('Mandatory `requester.url` key is missing')

    if not is_url(schema['url']):
        raise AuthenticationError('`requester.url` is not a valid URL')

    if 'method' not in schema:
        raise AuthenticationError('Mandatory `requester.method` key is missing')

    if not in_enum(schema['method'], HTTPMethod):
        raise AuthenticationError('`requester.method` is not a valid HTTP method')

    if not isinstance(schema.get('headers'), dict):
        raise AuthenticationError('`requester.headers` must be a dictionary')

    if not isinstance(schema.get('cookies'), dict):
        raise AuthenticationError('`requester.cookies` must be a dictionary')

    return AuthRequester(
        url=schema['url'],
        method=schema['method'],
        body=schema.get('body'),
        headers=schema.get('headers', {}),
        cookies=schema.get('cookies', {}),
    )


def _parse_extractor(schema: dict) -> AuthExtractor:
    """This function parses the extract schema and checks if all the necessary fields exist."""

    if 'key' not in schema:
        raise AuthenticationError('Mandatory `extractor.key` key is missing')

    if not isinstance(schema['key'], str):
        raise AuthenticationError('`extractor.key` must be a string')

    if 'location' not in schema:
        raise AuthenticationError('Mandatory `extractor.location` key is missing')

    if not in_enum(schema['location'], HTTPLocation):
        raise AuthenticationError('`extractor.location` is not a valid HTTP location')

    return AuthExtractor(
        key=schema['key'],
        location=schema['location'],
    )


def _parse_injector(schema: dict) -> AuthInjector:
    """This function parses the inject schema and checks if all the necessary fields exist."""

    if 'key' not in schema:
        raise AuthenticationError('Mandatory `injector.key` key is missing')

    if not isinstance(schema['key'], str):
        if not all(isinstance(key, str) for key in schema['key']):
            raise AuthenticationError('`injector.key` must be a list of strings or a string')

    if 'location' not in schema:
        raise AuthenticationError('Mandatory `injector.location` key is missing')

    if 'prefix' not in schema:
        raise AuthenticationError('Mandatory `injector.prefix` key is missing')

    return AuthInjector(
        key=schema['key'],
        location=schema['location'],
        prefix=schema['prefix'],
    )


def _parse_refresher(
    schema: dict,
    requester: AuthRequester,
    extractor: AuthExtractor,
    injector: AuthInjector,
) -> AuthProvider:
    """The parser is a bit lightweight (we should check the types of every keys)"""

    return AuthProvider(
        requester=AuthRequester(
            url=schema['refresh']['input'].get('url') or requester.url,
            method=schema['refresh']['input'].get('method') or requester.method,
            body=schema['refresh']['input'].get('body') or requester.body,
            cookies=schema['refresh']['input'].get('cookies') or requester.cookies,
            headers=schema['refresh']['input']['headers'].get('headers') or requester.headers,
        ),
        extractor=AuthExtractor(
            key=schema['refresh']['extract'].get('key') or extractor.key,
            location=schema['refresh']['extract'].get('location') or extractor.location,
        ),
        injector=AuthInjector(
            key=schema['refresh']['inject'].get('key') or injector.key,
            location=schema['refresh']['inject'].get('location') or injector.location,
            prefix=schema['refresh']['inject'].get('prefix') or injector.prefix,
        ),
        refresher=None,
    )


def parse_config(schema: dict) -> AuthProvider:
    """This function parses the Rest schema and checks if all the necessary fields exist."""

    if 'requester' not in schema:
        raise AuthenticationError('Mandatory `requester` key is missing')

    requester = _parser_requester(schema['requester'])

    if 'extractor' not in schema:
        raise AuthenticationError('Mandatory `extractor` key is missing')

    extractor = _parse_extractor(schema['extractor'])

    if 'injector' not in schema:
        raise AuthenticationError('Mandatory `injector` key is missing')

    injector = _parse_injector(schema['injector'])

    refresher = None
    if 'refresher' in schema:
        refresher = _parse_refresher(schema, requester, extractor, injector)

    return AuthProvider(requester=requester, extractor=extractor, injector=injector, refresher=refresher)


def attach_auth(
    user: User,
    auth_config: AuthProvider,
    proxy: str | None = None,
) -> AuthResponse:
    """This function takes the credentials of the user and authenticates them on the authentication URL."""

    if user and auth_config and proxy:  # TODO(antoine@escape.tech): remove this and code the function
        raise AuthenticationError('Cannot use proxy with user credentials')

    return AuthResponse(tech=AuthTech.REST, headers={})


def http_authenticator(
    user: User,
    schema: Dict,
    proxy: str | None = None,
) -> AuthResponse:
    """This funciton is a wrapper function that implements the Rest authentication schema.

    It takes the credentials of the user and authenticates them on the authentication URL.
    After authenticating, it fetches the token and adds the token to the
    headers along with optional headers in case the user provided them.
    """

    auth_config = parse_config(schema)
    return attach_auth(user, auth_config, proxy=proxy)
