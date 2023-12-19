import argparse
import json
import shlex
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from urllib.parse import urlparse

from multiauth.entities.http import HTTPMethod

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


class HttpScheme(StrEnum):
    HTTP = 'http'
    HTTPS = 'https'


def parse_scheme(raw_scheme: Any) -> HttpScheme:
    if not raw_scheme or not isinstance(raw_scheme, str):
        raise ValueError('Provided scheme is not set or not a string. Valid schemes are "http" and "https"')
    scheme = raw_scheme.lower()
    if scheme == HttpScheme.HTTP.value:
        return HttpScheme.HTTP
    if scheme == HttpScheme.HTTPS.value:
        return HttpScheme.HTTPS
    raise ValueError('Input is not cURL command with a valid scheme. Valid schemes are "http" and "https"')


def parse_method(raw_method: Any) -> HTTPMethod:
    if not isinstance(raw_method, str):
        raise ValueError('Provided method is not cURL command with a valid method.')
    if not raw_method:
        return 'GET'
    raw_method = raw_method.upper()
    if raw_method == 'POST':
        return 'POST'
    if raw_method == 'PUT':
        return 'PUT'
    if raw_method == 'DELETE':
        return 'DELETE'
    if raw_method == 'PATCH':
        return 'PATCH'
    if raw_method == 'HEAD':
        return 'HEAD'
    if raw_method == 'OPTIONS':
        return 'OPTIONS'
    if raw_method == 'TRACE':
        return 'TRACE'
    if raw_method == 'CONNECT':
        return 'CONNECT'

    raise ValueError(
        f'Invalid method {raw_method.upper()}',
    )


def parse_query_params(raw_query_params: Any) -> dict[str, str]:
    raw_query_params = raw_query_params or ''

    query_params: dict[str, str] = {}
    for raw in raw_query_params.split('&'):
        if raw == '':
            return query_params
        key, value = raw.split('=')
        if not key or not value:
            raise ValueError('Invalid query parameters.')
        query_params[key] = value
    return query_params


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


JSONSerializable = dict | list | str | int | float | bool | None


def parse_data(raw_data: Any) -> tuple[str, JSONSerializable | None]:
    if not raw_data or not isinstance(raw_data, str):
        raise ValueError('Provided data payload is not set or is not a string.')
    try:
        body = json.loads(raw_data)
        return raw_data, body
    except json.JSONDecodeError:
        return raw_data, None


def parse_cookies(raw_cookies: Any) -> dict[str, str]:
    raw_cookies = raw_cookies or []
    cookies: dict[str, str] = {}

    for cookie in raw_cookies:
        if not isinstance(cookie, str):
            continue
        try:
            key, value = cookie.split('=', 1)
        except ValueError:
            pass
        else:
            cookies[key] = value

    return cookies


def parse_headers(raw_headers: Any) -> dict[str, str]:
    raw_headers = raw_headers or []
    headers = {}

    for raw_header in raw_headers:
        if not isinstance(raw_header, str):
            continue
        try:
            key, value = raw_header.split(':', 1)
            value = value.strip()
        except ValueError:
            pass
        else:
            headers[key] = value

    return headers


@dataclass
class HttpRequest:
    method: HTTPMethod
    host: str
    scheme: HttpScheme
    path: str = '/'
    headers: dict[str, str] = field(default_factory=dict)
    username: str | None = None
    password: str | None = None
    json: JSONSerializable | None = None
    data: str | None = None
    query_parameters: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    timeout: int = 5

    @staticmethod
    def from_curl(curl: str) -> 'HttpRequest':
        """Parse a curl command into a HTTPRequest object."""

        cookies: dict[str, str] = {}
        headers: dict[str, str] = {}
        method: HTTPMethod = 'GET'

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
        query_parameters = parse_query_params(url.query)
        cookies = parse_cookies(parsed_args.cookie)
        headers = parse_headers(parsed_args.header)
        username, password = parse_user(parsed_args.user)

        data = parsed_args.data
        if data:
            method = 'POST'
            data, json = parse_data(data)
        else:
            data, json = None, None

        return HttpRequest(
            method=method,
            scheme=scheme,
            host=url.netloc,
            path=path,
            headers=headers,
            query_parameters=query_parameters,
            username=username,
            password=password,
            json=json,
            data=data,
            cookies=cookies,
        )
