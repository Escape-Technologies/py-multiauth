import argparse
import json
import shlex
from http import HTTPMethod
from typing import Any, TypeVar
from urllib.parse import parse_qs, urlparse

from multiauth.entities.curl import ParsedCurlContent, RawCredentials
from multiauth.entities.http import HTTPRequest, JSONSerializable, parse_method, parse_scheme

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


def parse_curl(curl: str) -> HTTPRequest:
    """Parse a curl command into a HTTPRequest object."""

    cookies: dict[str, str] = {}
    headers: dict[str, str] = {}
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
        query_parameters=parse_qs(url.query),
        username=username,
        password=password,
        data_json=json,
        data_text=data,
        cookies=cookies,
        proxy=None,
    )


Default = TypeVar('Default')
Value = TypeVar('Value')


# pylint: disable=too-many-branches
def uncurl(curl: str) -> ParsedCurlContent:
    """This is a function that takes a curl as an input and analyses it."""

    parser = argparse.ArgumentParser()
    parser.add_argument('curl', help='The command curl that is analyzed in the string')
    parser.add_argument('url', help='The URL on which the curl command is working on')
    parser.add_argument(
        '-H',
        '--header',
        action='append',
        default=[],
        help='The header that are added to every request',
    )
    parser.add_argument('-X', '--request', help='the HTTP method used')
    parser.add_argument('-u', '--user', default=(), help='Specify the username password in the server authentication')
    parser.add_argument(
        '-A',
        '--user-agent',
        help='This specifies the user agent, if the value if empty than user agent will be removed from the headers',
    )
    parser.add_argument('--request-target', help='Gives the path of the target it wants to curl to')
    parser.add_argument('-e', '--referer', help='Gives the referer used in the header')
    parser.add_argument(
        '-d',
        '--data',
        '--data-binary',
        '--data-raw',
        '--data-urlencode',
        action='append',
        default=[],
        help='Data sent',
    )
    parser.add_argument('-k', '--insecure', action='store_true')

    # First we need to prepare the curl for parsing
    result_curl: list[str] = shlex.split(curl.replace('\\\n', ''))

    # Now we have to parse the curl command
    parsed_args, _ = parser.parse_known_args(result_curl)

    # Now we have to analyze what we have
    # First find out what type of method are we using
    method: HTTPMethod = HTTPMethod.GET
    if parsed_args.request:
        method = HTTPMethod(parsed_args.request.upper())
    else:
        if parsed_args.data:
            method = HTTPMethod.POST
        else:
            method = HTTPMethod.GET

    # Now we have to extract the headers
    headers: dict[str, str] = {}
    for header in parsed_args.header:
        param_prefix, header_value = header.split(':', 1)
        headers[param_prefix] = header_value.strip()

    if parsed_args.user_agent:
        headers['User-Agent'] = parsed_args.user_agent

    if parsed_args.referer:
        headers['Referer'] = parsed_args.user_agent

    datas: list = parsed_args.data
    final_data: str | None = None
    if len(datas) != 0:
        final_data = datas[0]
    if len(datas) != 1:
        for data in datas[1:]:
            final_data += '&' + data

    url: str = ''
    if parsed_args.request_target:
        parsed_url = urlparse(parsed_args.url)
        if parsed_args.request_target[-1] == '/':
            url = parsed_url.scheme + '://' + parsed_url.netloc + parsed_args.request_target
        else:
            url = parsed_url.scheme + '://' + parsed_url.netloc + '/' + parsed_args.request_target
    else:
        url = parsed_args.url

    # Add auth
    credentials: RawCredentials | None = None
    if parsed_args.user:
        user_name, password = parsed_args.user.split(':', 1)
        credentials = RawCredentials(username=user_name, password=password)

    return ParsedCurlContent(method=method, url=url, data=final_data, headers=headers, credentials=credentials)
