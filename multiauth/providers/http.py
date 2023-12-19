"""Implementation of the HTTP authentication schema."""

import json
from typing import Dict, cast
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests

from multiauth.entities.errors import AuthenticationError
from multiauth.entities.providers.http import (
    AuthExtractor,
    AuthRequester,
    Credentials,
    HTTPLocation,
    HTTPRequest,
    HTTPResponse,
    HTTPScheme,
)
from multiauth.manager import User
from multiauth.providers.http_parser import parse_config
from multiauth.utils import deep_merge_data, dict_find_path, dict_nested_get

TIMEOUT = 5


def _format_request(requester: AuthRequester, credential: Credentials, proxy: str | None) -> HTTPRequest:
    url = requester.url
    method = requester.method

    headers = requester.headers | credential.headers
    cookies = requester.cookies | credential.cookies

    data = deep_merge_data(requester.body, credential.body)

    parsed_url = urlparse(url)
    return HTTPRequest(
        method=method,
        host=parsed_url.netloc,
        scheme=HTTPScheme(parsed_url.scheme.upper()),
        path=parsed_url.path,
        headers=headers,
        username=None,
        password=None,
        data=json.dumps(data),
        json=data,
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
        data=req.data,
        timeout=TIMEOUT,
        proxies={'http': req.proxy, 'https': req.proxy} if req.proxy else None,
    )

    return HTTPResponse(
        url=response.url,
        status_code=response.status_code,
        reason=response.reason,
        headers=dict(response.headers),
        cookies=response.cookies.get_dict(),  # type: ignore[no-untyped-call]
        data=response.text,
        json=response.json(),
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
            res.json,
        )  # TODO(antoine@escape.tech): This makes the assertion that a valid request will always return a JSON
        path = dict_find_path(body, extractor.key, '')
        return dict_nested_get(body, path)

    raise AuthenticationError(f'We could not find any key `{extractor.key}` nested in the response')


def user_to_credentials(user: User) -> Credentials:
    """This function converts the user to credentials."""

    return Credentials(
        name=str(user.credentials),
        headers={},
        cookies={},
        body={},
    )


def http_authenticator(
    user: User,
    schema: Dict,
    proxy: str | None = None,
) -> None:
    """This funciton is a wrapper function that implements the Rest authentication schema.

    It takes the credentials of the user and authenticates them on the authentication URL.
    After authenticating, it fetches the token and adds the token to the
    headers along with optional headers in case the user provided them.
    """

    creds = user_to_credentials(user)

    auth_provider = parse_config(schema)
    req, res = send_request(auth_provider.requester, creds, proxy)
    _ = extract_token(auth_provider.extractor, res)

    return
