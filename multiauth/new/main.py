"""Implementation of the HTTP authentication schema."""

import json
from typing import cast
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests

from multiauth.entities.errors import AuthenticationError
from multiauth.entities.http import HTTPCookies, HTTPHeaders, HTTPLocation, HTTPRequest, HTTPResponse
from multiauth.entities.main import AuthResponse, AuthTech
from multiauth.entities.user import UserName
from multiauth.helpers.curl import parse_scheme
from multiauth.new.entities.main import AuthExtractor, AuthInjector, AuthProvider, AuthRequester, Credentials
from multiauth.new.parser import parse_config
from multiauth.utils import deep_merge_data, dict_find_path, dict_nested_get, merge_headers

TIMEOUT = 5


def _format_request(requester: AuthRequester, credential: Credentials, proxy: str | None) -> HTTPRequest:
    url = requester.url
    method = requester.method

    headers = merge_headers(requester.headers, credential.headers)
    cookies = merge_headers(requester.cookies, credential.cookies)

    data = deep_merge_data(requester.body, credential.body)

    parsed_url = urlparse(url)
    return HTTPRequest(
        method=method,
        host=parsed_url.netloc,
        scheme=parse_scheme(parsed_url.scheme),
        path=parsed_url.path,
        headers=headers,
        username=None,
        password=None,
        data_text=json.dumps(data),
        data_json=data,
        query_parameters=parse_qs(parsed_url.query),
        cookies=cookies,
        proxy=proxy,
        timeout=TIMEOUT,
    )


def _send_request(req: HTTPRequest) -> HTTPResponse:
    """This function converts the request to a proto object."""

    url = urlunparse((req.scheme.value, req.host, req.path, '', urlencode(req.query_parameters), ''))

    response = requests.request(
        req.method.value,
        url,
        headers=req.headers,
        cookies=req.cookies,
        data=req.data_text,
        timeout=TIMEOUT,
        proxies={'http': req.proxy, 'https': req.proxy} if req.proxy else None,
    )

    data_json = None
    try:
        data_json = response.json()
    except json.JSONDecodeError:
        pass

    return HTTPResponse(
        url=response.url,
        status_code=response.status_code,
        reason=response.reason,
        headers=dict(response.headers),
        cookies={cookie.name: cookie.value for cookie in response.cookies if cookie.value is not None},
        data_text=response.text,
        data_json=data_json,
        elapsed=response.elapsed,
    )


def send_request(
    requester: AuthRequester,
    credential: Credentials,
    proxy: str | None,
) -> tuple[HTTPRequest, HTTPResponse]:
    """Send request from the requester and credential."""

    req = _format_request(requester, credential, proxy)
    res = _send_request(req)

    return req, res


def extract_token(extractor: AuthExtractor, res: HTTPResponse) -> str:
    """This function extracts the token from the response."""

    if extractor.location == HTTPLocation.HEADER:
        return res.headers[extractor.key]

    if extractor.location == HTTPLocation.COOKIE:
        return res.cookies[extractor.key]

    if extractor.location == HTTPLocation.BODY:
        body = cast(
            dict,
            res.data_json,
        )  # TODO(antoine@escape.tech): This makes the assertion that a valid request will always return a JSON
        path = dict_find_path(body, extractor.key, '')
        return dict_nested_get(body, path)

    raise AuthenticationError(f'We could not find any key `{extractor.key}` nested in the response')


def inject_token(injector: AuthInjector, username: str, token: str, set_cookies: dict[str, str]) -> Credentials:
    """This function injects the token in the request.

    It also takes the response as input as response.cookies actually contains the parsed cookies that are returned
    in the "Set-Cookie" header of the response and that should be returned to the server
    """

    token_value = f'{injector.prefix.strip()} {token}' if injector.prefix else token

    if injector.location == HTTPLocation.HEADER:
        return Credentials(
            name=UserName(username),
            headers=HTTPHeaders({injector.key: token_value}),
            cookies=HTTPCookies(set_cookies),
            body=None,
        )

    if injector.location == HTTPLocation.COOKIE:
        return Credentials(
            name=UserName(username),
            headers=HTTPHeaders({}),
            body=None,
            cookies=HTTPCookies(merge_headers(set_cookies, {injector.key: token_value})),
        )

    raise AuthenticationError(f'We could not find any key `{injector.key}` nested in the response')


def http_standard_flow(
    provider: AuthProvider,
    tech: AuthTech,
    credentials: Credentials,
    proxy: str | None,
) -> AuthResponse:
    """This function is a wrapper function that implements the Rest authentication schema.

    It takes the credentials of the user and authenticates them on the authentication URL.
    After authenticating, it fetches the token and adds the token to the
    headers along with optional headers in case the user provided them.
    """

    if provider.requester is None or provider.extractor is None or provider.injector is None:
        raise AuthenticationError('The auth provider is not properly configured')

    req, res = send_request(provider.requester, credentials, proxy)
    token = extract_token(provider.extractor, res)
    credentials = inject_token(provider.injector, credentials.name, token, res.cookies)

    return AuthResponse(
        name=credentials.name,
        headers=credentials.headers,
        cookies=credentials.cookies,
        body=credentials.body,
        tech=tech,
    )


def http_authenticator(
    credentials: Credentials,
    schema: dict,
    proxy: str | None = None,
) -> AuthResponse:
    """This funciton is a wrapper function that implements the Rest authentication schema.

    It takes the credentials of the user and authenticates them on the authentication URL.
    After authenticating, it fetches the token and adds the token to the
    headers along with optional headers in case the user provided them.
    """

    auth_provider = parse_config(schema)
    return http_standard_flow(auth_provider, AuthTech.REST, credentials, proxy)
