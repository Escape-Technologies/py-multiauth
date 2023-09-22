import itertools
import logging
import re
from typing import Any

logger = logging.getLogger('multiauth.providers.webdriver.extractors')


def extract_from_request_url(requests: Any, rx: str) -> list[str]:
    res = []

    for request in requests:
        if match := re.search(rx, request.url):  # type: ignore[syntax]
            res.append(match.group(1))

    return res


def extract_from_request_header(requests: Any, rx: str) -> list[str]:
    res = []

    for header in itertools.chain.from_iterable(request.headers for request in requests):
        if match := re.search(rx, header):
            res.append(match.group(1))

    return res


def extract_from_response_header(requests: Any, rx: str) -> list[str]:
    res = []
    for header in itertools.chain.from_iterable(request.response.headers for request in requests if request.response):
        if match := re.search(rx, header):
            res.append(match.group(1))

    return res


def extract_from_request_body(requests: Any, rx: str) -> list[str]:
    res = []
    for request in requests:
        if match := re.search(rx, request.body.decode()):
            res.append(match.group(1))

    return res


def extract_from_response_body(requests: Any, rx: str) -> list[str]:
    res = []
    for request in requests:
        if not request.response:
            continue
        try:
            if match := re.search(rx, request.response.body.decode()):
                res.append(match.group(1))
        except Exception as e:
            logger.debug(f'Skipping {request.url} due to error {e}')

    return res


def extract_token(location: str, rx: str, index: int | None, requests: list) -> str:
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
        tks = extract_from_request_url(requests, rx)
    elif location == locations[1]:
        tks = extract_from_request_header(requests, rx)
    elif location == locations[2]:
        tks = extract_from_request_body(requests, rx)
    elif location == locations[3]:
        tks = extract_from_response_header(requests, rx)
    elif location == locations[4]:
        tks = extract_from_response_body(requests, rx)

    if not tks:
        raise ValueError('No token found.')

    index = index or 0
    logger.info(f'Found {len(tks)} tokens in `{location}` with regex `{rx}`. Taking index `{index}`')

    return tks[index]
