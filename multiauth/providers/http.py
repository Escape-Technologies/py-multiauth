"""Implementation of the Rest authentication schema."""

import json
from typing import Dict
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import requests

from multiauth.entities.providers.http import (
    AuthRequester,
    Credentials,
    HTTPRequest,
    HTTPResponse,
    HTTPScheme,
)
from multiauth.manager import User
from multiauth.providers.http_parser import parse_config
from multiauth.utils import deep_merge_data

TIMEOUT = 5


def send_request(req: HTTPRequest) -> requests.Response:
    """This function converts the request to a proto object."""

    url = urlunparse((req.scheme.value, req.host, req.path, '', urlencode(req.query_parameters), ''))

    return requests.request(
        req.method.value,
        url,
        headers=req.headers,
        cookies=req.cookies,
        data=req.data,
        timeout=TIMEOUT,
        proxies={'http': req.proxy, 'https': req.proxy} if req.proxy else None,
    )


def response_to_proto(response: requests.Response) -> HTTPResponse:
    """This function converts the response to a proto object."""

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


def send_http_request(
    requester: AuthRequester,
    credential: Credentials,
    proxy: str | None,
) -> tuple[HTTPRequest, HTTPResponse]:
    url = requester.url
    method = requester.method

    headers = requester.headers | credential.headers
    cookies = requester.cookies | credential.cookies

    data = deep_merge_data(requester.body, credential.body)

    parsed_url = urlparse(url)
    req = HTTPRequest(
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

    res = send_request(req)

    return req, response_to_proto(res)


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
    req, res = send_http_request(auth_provider.requester, creds, proxy)
