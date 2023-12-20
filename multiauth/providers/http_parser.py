"""Implementation of the Rest authentication schema."""

from http import HTTPMethod

from multiauth.entities.errors import AuthenticationError
from multiauth.entities.providers.http import (
    AuthExtractor,
    AuthInjector,
    AuthProvider,
    AuthRefresher,
    AuthRequester,
    Credentials,
    HTTPLocation,
)
from multiauth.utils import in_enum, is_url


def parser_requester(schema: dict) -> AuthRequester:
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


def parse_extractor(schema: dict) -> AuthExtractor:
    """This function parses the extract schema and checks if all the necessary fields exist."""

    if 'key' not in schema:
        raise AuthenticationError('Mandatory `extractor.key` key is missing')

    if not isinstance(schema['key'], str):
        raise AuthenticationError('`extractor.key` must be a string')

    if 'param_location' not in schema:
        raise AuthenticationError('Mandatory `extractor.location` key is missing')

    if not in_enum(schema['param_location'], HTTPLocation):
        raise AuthenticationError('`extractor.location` is not a valid HTTP location')

    return AuthExtractor(
        key=schema['key'],
        location=schema['param_location'],
    )


def parse_injector(schema: dict) -> AuthInjector:
    """This function parses the inject schema and checks if all the necessary fields exist."""

    if 'key' not in schema:
        raise AuthenticationError('Mandatory `injector.key` key is missing')

    if not isinstance(schema['key'], str):
        if not all(isinstance(key, str) for key in schema['key']):
            raise AuthenticationError('`injector.key` must be a list of strings or a string')

    if 'param_location' not in schema:
        raise AuthenticationError('Mandatory `injector.location` key is missing')

    if 'prefix' not in schema:
        raise AuthenticationError('Mandatory `injector.prefix` key is missing')

    return AuthInjector(
        key=schema['key'],
        location=schema['param_location'],
        prefix=schema['prefix'],
    )


def parse_refresher(
    schema: dict,
    requester: AuthRequester,
    extractor: AuthExtractor,
    injector: AuthInjector,
) -> AuthRefresher:
    """The parser is a bit lightweight (we should check the types of every keys)"""

    return AuthRefresher(
        requester=AuthRequester(
            url=schema['refresh']['input'].get('url') or requester.url,
            method=schema['refresh']['input'].get('method') or requester.method,
            body=schema['refresh']['input'].get('body') or requester.body,
            cookies=schema['refresh']['input'].get('cookies') or requester.cookies,
            headers=schema['refresh']['input']['headers'].get('headers') or requester.headers,
        ),
        extractor=AuthExtractor(
            key=schema['refresh']['extract'].get('key') or extractor.key,
            location=schema['refresh']['extract'].get('param_location') or extractor.location,
        ),
        injector=AuthInjector(
            key=schema['refresh']['inject'].get('key') or injector.key,
            location=schema['refresh']['inject'].get('param_location') or injector.location,
            prefix=schema['refresh']['inject'].get('prefix') or injector.prefix,
        ),
    )


def parse_config(schema: dict) -> AuthProvider:
    """This function parses the Rest schema and checks if all the necessary fields exist."""

    if 'requester' not in schema:
        raise AuthenticationError('Mandatory `requester` key is missing')

    requester = parser_requester(schema['requester'])

    if 'extractor' not in schema:
        raise AuthenticationError('Mandatory `extractor` key is missing')

    extractor = parse_extractor(schema['extractor'])

    if 'injector' not in schema:
        raise AuthenticationError('Mandatory `injector` key is missing')

    injector = parse_injector(schema['injector'])

    refresher = None
    if 'refresher' in schema:
        refresher = parse_refresher(schema, requester, extractor, injector)

    return AuthProvider(requester=requester, extractor=extractor, injector=injector, refresher=refresher)


def parse_credentials(schema: dict) -> Credentials:
    """This function parses the credentials schema and checks if all the necessary fields exist."""

    if 'name' not in schema:
        raise AuthenticationError('Mandatory `name` key is missing from credentials')

    if not isinstance(schema['name'], str):
        raise AuthenticationError('`name` must be a string in credentials')

    if 'headers' not in schema:
        raise AuthenticationError('Mandatory `headers` key is missing from credentials')

    if not isinstance(schema['headers'], dict):
        raise AuthenticationError('`headers` must be a dictionary in credentials')

    if 'cookies' not in schema:
        raise AuthenticationError('Mandatory `cookies` key is missing from credentials')

    if not isinstance(schema['cookies'], dict):
        raise AuthenticationError('`cookies` must be a dictionary in credentials')

    if 'body' not in schema:
        raise AuthenticationError('Mandatory `body` key is missing from credentials')

    if not isinstance(schema['body'], dict):
        raise AuthenticationError('`body` must be a dictionary in credentials')

    return Credentials(
        name=schema['name'],
        headers=schema['headers'],
        cookies=schema['cookies'],
        body=schema['body'],
    )
