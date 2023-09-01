import itertools
import logging
import re
from typing import Any

logger = logging.getLogger('multiauth.providers.webdriver.extractors')


def extract_from_request_url(requests: Any, rx: str) -> str | None:
    for request in requests:
        if match := re.search(rx, request.url):
            return match.group(1)

    return None


def extract_from_request_header(requests: Any, rx: str) -> str | None:
    for header in itertools.chain.from_iterable(request.headers for request in requests):
        if match := re.search(rx, header):
            return match.group(1)

    return None


def extract_from_response_header(requests: Any, rx: str) -> str | None:
    for header in itertools.chain.from_iterable(request.response.headers for request in requests if request.response):
        if match := re.search(rx, header):
            return match.group(1)

    return None


def extract_from_request_body(requests: Any, rx: str) -> str | None:
    for request in requests:
        if match := re.search(rx, request.body.decode()):
            return match.group(1)

    return None


def extract_from_response_body(requests: Any, rx: str) -> str | None:
    for request in requests:
        if not request.response:
            continue
        try:
            if match := re.search(rx, request.response.body.decode()):
                return match.group(1)
        except Exception as e:
            logger.debug(f'Skipping {request.url} due to error {e}')

    return None


def extract_token(location: str, rx: str, requests: Any) -> str:
    locations = [
        'RequestURL',
        'RequestHeader',
        'RequestBody',
        'ResponseHeader',
        'ResponseBody',
    ]

    if location not in locations:
        raise ValueError(f'Invalid location `{location}`, must be one of: {locations}')

    if location == locations[0]:
        tk = extract_from_request_url(requests, rx)
    elif location == locations[1]:
        tk = extract_from_request_header(requests, rx)
    elif location == locations[2]:
        tk = extract_from_request_body(requests, rx)
    elif location == locations[3]:
        tk = extract_from_response_header(requests, rx)
    elif location == locations[4]:
        tk = extract_from_response_body(requests, rx)

    if not tk:
        raise KeyError('Token not found')

    return tk
