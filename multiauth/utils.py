"""Utility functions independent of the library."""

import argparse
import logging
import os
import shlex
from enum import Enum
from typing import Any, Mapping, Type, TypeVar
from urllib.parse import urlparse

from pydash import py_

from multiauth.entities.http import HTTPMethod
from multiauth.entities.utils import Credentials, ParsedCurlContent

Default = TypeVar('Default')
Value = TypeVar('Value')


def is_url(url: str) -> bool:
    """This function checks if the url is valid."""

    if not isinstance(url, str):
        raise TypeError(f'Expected a string, got {type(url)}')

    parsed_url = urlparse(url)
    return bool(parsed_url.scheme and parsed_url.netloc)


def dict_deep_merge(dict1: dict, dict2: dict) -> dict:
    """
    Recursively merge two dictionaries, including nested dictionaries.
    """
    result = dict1.copy()  # Start with dict1's keys and values
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # If the key is in both dictionaries and both values are dicts, merge them
            result[key] = dict_deep_merge(result[key], value)
        else:
            # Otherwise, use dict2's value, overriding dict1's value if key is present
            result[key] = value
    return result


def merge_headers(headers1: dict[str, str], headers2: dict[str, str]) -> dict[str, str]:
    """This function merges two headers together."""

    headers1 = {k.lower(): v for k, v in headers1.items()}
    headers2 = {k.lower(): v for k, v in headers2.items()}

    headers: dict[str, str] = headers1.copy()  # Start with headers1

    for name, value in headers2.items():
        # Resolving duplicate keys
        if name in headers:
            headers[name] += f', {value}'
        else:
            headers[name] = value

    return headers


def deep_merge_data(base_data: Any, user_data: Any) -> Any:
    # If the base data is a dict, and the user data is a dict, then we merge them
    if isinstance(base_data, dict) and isinstance(user_data, dict):
        return dict_deep_merge(base_data, user_data)

    # If the base data is a list, and the user data is a list, then we merge them
    if isinstance(base_data, list) and isinstance(user_data, list):
        return base_data + user_data

    if user_data is None:
        return base_data

    # In any other case, user_data prevails over base_data
    return user_data


def in_enum(method: str, myenum: Type[Enum]) -> bool:
    """This function checks if the http method is valid."""

    try:
        myenum(method.upper())
        return True
    except ValueError:
        return False


def install_logger(logger: logging.Logger) -> None:
    """Install logger."""

    handler = logging.StreamHandler()

    formatter = os.getenv('LOG_FMT') or '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler.setFormatter(logging.Formatter(formatter))

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if os.getenv('DEBUG') else logging.INFO)

    # Ignore asyncio debug logs
    logging.getLogger('asyncio').setLevel(logging.ERROR)


def setup_logger(name: str | None = None) -> logging.Logger:
    """Setup logger."""

    name = name or 'multiauth'
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        install_logger(logger)

    return logger


def dict_find_path(
    nested_dict: Mapping,
    key: str,
    prepath: str = '',
    index: int | None = None,
) -> str:
    """Recursively find the path of a certain key in a dict."""

    for k, v in nested_dict.items():
        if prepath == '':
            path = k
        elif index is not None:
            path = f'{prepath}.{index}.{k}'
        else:
            path = f'{prepath}.{k}'

        if k == key:  # found value
            return path

        if isinstance(v, dict):
            p = dict_find_path(v, key, path, None)  # recursive call
            if p != '':
                return p

        if isinstance(v, list):
            for i, elem in enumerate(v):
                if isinstance(elem, dict):
                    p = dict_find_path(elem, key, path, i)
                    if p != '':
                        return p

    return ''


def dict_nested_get(
    dictionary: Mapping[str, Value],
    key: str,
    default_return: Default | None = None,
) -> Default | Value:
    """Search for a certain key inside a dict and returns its value (no matter the depth)"""
    return py_.get(dictionary, dict_find_path(dictionary, key, ''), default_return)


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
    method: HTTPMethod = 'GET'
    if parsed_args.request:
        method = parsed_args.request.upper()
    else:
        if parsed_args.data:
            method = 'POST'
        else:
            method = 'GET'

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
    credentials: Credentials | None = None
    if parsed_args.user:
        user_name, password = parsed_args.user.split(':', 1)
        credentials = Credentials(user_name, password)

    return ParsedCurlContent(method, url, final_data, headers, credentials)
