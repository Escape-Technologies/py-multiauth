import argparse
import json
import shlex
from http import HTTPMethod
from typing import Any
from urllib.parse import parse_qs, urlparse

from multiauth.lib.http_core.entities import (
    HTTPCookie,
    HTTPHeader,
    HTTPQueryParameter,
    HTTPRequest,
    HTTPScheme,
    JSONSerializable,
)

parser = argparse.ArgumentParser()

parser.add_argument('command')
parser.add_argument('url')
parser.add_argument('-A', '--user-agent')
parser.add_argument('-I', '--head')
parser.add_argument('-H', '--header', action='append', default=[])
parser.add_argument('-b', '--cookie', action='append', default=[])
parser.add_argument('-d', '--data', '--data-ascii', '--data-binary', '--data-raw', default=None)
parser.add_argument('-k', '--insecure', action='store_false')
parser.add_argument('-u', '--user', default=())
parser.add_argument('-X', '--request', default='')
parser.add_argument('-x', '--proxy', default=None)

"""Multiauth types related to HTTP protocol."""


def parse_method(raw_method: Any) -> HTTPMethod:
    if not isinstance(raw_method, str):
        raise ValueError('Provided method is not cURL command with a valid method.')
    if not raw_method:
        return HTTPMethod.GET
    raw_method = raw_method.upper()
    try:
        return HTTPMethod(raw_method)
    except ValueError as e:
        raise ValueError(
            f'Invalid method {raw_method.upper()}',
        ) from e


def parse_scheme(raw_scheme: Any) -> HTTPScheme:
    if not raw_scheme or not isinstance(raw_scheme, str):
        raise ValueError('Provided scheme is not set or not a string. Valid schemes are "http" and "https"')
    scheme = raw_scheme.lower()
    if scheme == HTTPScheme.HTTP.value:
        return HTTPScheme.HTTP
    if scheme == HTTPScheme.HTTPS.value:
        return HTTPScheme.HTTPS
    raise ValueError('Input is not cURL command with a valid scheme. Valid schemes are "http" and "https"')


def parse_user(raw_user: Any) -> tuple[str | None, str | None]:
    if not raw_user or not isinstance(raw_user, str):
        return None, None
    username = None
    password = None

    username, password = tuple(raw_user.split(':'))
    if not password or not isinstance(password, str):
        password = None
    if not username or not isinstance(username, str):
        username = None
    return username, password


def parse_data(raw_data: Any) -> tuple[str, JSONSerializable | None]:
    if not raw_data or not isinstance(raw_data, str):
        raise ValueError('Provided data payload is not set or is not a string.')
    try:
        body = json.loads(raw_data)
        return raw_data, body
    except json.JSONDecodeError:
        return raw_data, None


def parse_query_parameters(raw_query_parameters: str) -> list[HTTPQueryParameter]:
    res = list[HTTPQueryParameter]()
    qp = parse_qs(raw_query_parameters)

    for key, values in qp.items():
        res.append(HTTPQueryParameter(name=key, values=values))

    return res


def parse_cookies(raw_cookies: Any) -> list[HTTPCookie]:
    raw_cookies = raw_cookies or []
    cookies = list[HTTPCookie]()

    for raw_cookie in raw_cookies:
        if not isinstance(raw_cookie, str):
            continue
        try:
            key, value = raw_cookie.split('=', 1)
        except ValueError:
            continue

        # Check if cookie already exists
        existing_cookie = next((cookie for cookie in cookies if cookie.name == key), None)
        if existing_cookie:
            existing_cookie.values.append(value)
        else:
            cookies.append(HTTPCookie(name=key, values=[value]))

    return cookies


def parse_headers(raw_headers: Any) -> list[HTTPHeader]:
    raw_headers = raw_headers or []
    headers = list[HTTPHeader]()

    for raw_header in raw_headers:
        if not isinstance(raw_header, str):
            continue
        try:
            key, value = raw_header.split(':', 1)
            value = value.strip()
        except ValueError:
            continue

        # Check if header already exists
        existing_header = next((header for header in headers if header.name == key), None)
        if existing_header:
            existing_header.values.append(value)
        else:
            headers.append(HTTPHeader(name=key, values=[value]))

    return headers


def parse_curl(curl: str) -> HTTPRequest:
    """Parse a curl command into a HTTPRequest object."""

    cookies = list[HTTPCookie]()
    headers = list[HTTPHeader]()
    method: HTTPMethod = HTTPMethod.GET

    curl = curl.replace('\\\n', ' ')

    tokens = shlex.split(curl)
    parsed_args = parser.parse_args(tokens)

    if parsed_args.command != 'curl':
        raise ValueError('Input is not a valid cURL command')

    try:
        raw_url = parsed_args.url
        if not isinstance(raw_url, str):
            raise ValueError('Input is not cURL command with a valid URL')
        if not raw_url.startswith('http://') and not raw_url.startswith('https://'):
            raw_url = 'http://' + raw_url
        url = urlparse(raw_url)
    except Exception as e:
        raise ValueError('Input is not cURL command with a valid URL') from e

    scheme = parse_scheme(url.scheme)
    path = url.path or '/'
    method = parse_method(raw_method=parsed_args.request)
    cookies = parse_cookies(parsed_args.cookie)
    headers = parse_headers(parsed_args.header)
    username, password = parse_user(parsed_args.user)
    query_parameters = parse_query_parameters(url.query)
    proxy = parsed_args.proxy

    data = parsed_args.data
    if data:
        method = HTTPMethod.POST
        data, json = parse_data(data)
    else:
        data, json = None, None

    return HTTPRequest(
        method=method,
        scheme=scheme,
        host=url.netloc,
        path=path,
        headers=headers,
        query_parameters=query_parameters,
        username=username,
        password=password,
        data_json=json,
        data_text=data,
        cookies=cookies,
        proxy=proxy,
    )
