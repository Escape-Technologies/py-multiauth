"""Utility functions independent of the library."""

import argparse
import logging
import os
import shlex
from typing import Dict, List, Mapping, Optional, TypeVar, Union
from urllib.parse import urlparse

from pydash import py_

from multiauth.entities.http import HTTPMethod
from multiauth.entities.utils import Credentials, ParsedCurlContent

Default = TypeVar('Default')
Value = TypeVar('Value')


def install_logger(logger: logging.Logger) -> None:
    """Install logger."""

    handler = logging.StreamHandler()

    formatter = os.getenv('LOG_FMT') or '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler.setFormatter(logging.Formatter(formatter))

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if os.getenv('DEBUG') else logging.INFO)

    # Ignore asyncio debug logs
    logging.getLogger('asyncio').setLevel(logging.ERROR)


def setup_logger(name: Optional[str] = None) -> logging.Logger:
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
    index: Optional[int] = None,
) -> str:
    """Recursively find the path of a certain key in a Dict."""

    for k, v in nested_dict.items():
        if prepath == '':
            path = k
        elif index is not None:
            path = f'{prepath}.{index}.{k}'
        else:
            path = f'{prepath}.{k}'

        if k == key:  # found value
            return path

        if isinstance(v, Dict):
            p = dict_find_path(v, key, path, None)  # recursive call
            if p != '':
                return p

        if isinstance(v, List):
            for i, elem in enumerate(v):
                if isinstance(elem, Dict):
                    p = dict_find_path(elem, key, path, i)
                    if p != '':
                        return p

    return ''


def dict_nested_get(
    dictionary: Mapping[str, Value],
    key: str,
    default_return: Optional[Default] = None,
) -> Union[Default, Value]:
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
    result_curl: List[str] = shlex.split(curl.replace('\\\n', ''))

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
    headers: Dict[str, str] = {}
    for header in parsed_args.header:
        header_prefix, header_value = header.split(':', 1)
        headers[header_prefix] = header_value.strip()

    if parsed_args.user_agent:
        headers['User-Agent'] = parsed_args.user_agent

    if parsed_args.referer:
        headers['Referer'] = parsed_args.user_agent

    datas: list = parsed_args.data
    final_data: Optional[str] = None
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
    credentials: Optional[Credentials] = None
    if parsed_args.user:
        user_name, password = parsed_args.user.split(':', 1)
        credentials = Credentials(user_name, password)

    return ParsedCurlContent(method, url, final_data, headers, credentials)
