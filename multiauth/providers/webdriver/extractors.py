import enum
import logging
import re
from typing import Any

from multiauth.entities.errors import AuthenticationError

logger = logging.getLogger('multiauth.providers.webdriver.extractors')


def extract_from_request_url(requests: Any, rx: str) -> list[str]:
    res = []

    for request in requests:
        if match := re.search(rx, request.url):
            res.append(match.group(1))

    return res


def extract_from_request_header(requests: Any, rx: str) -> list[str]:
    res = []

    for request in requests:
        for header, header_value in request.headers.items():
            if match := re.search(rx, header + ': ' + header_value):
                res.append(match.group(1))

    return res


def extract_from_response_header(requests: Any, rx: str) -> list[str]:
    res = []
    for request in requests:
        if not request.response:
            continue
        for header, header_value in request.response.headers.items():
            if match := re.search(rx, header + ': ' + header_value):
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


class ExchangeLocation(enum.StrEnum):
    REQUEST_URL = 'RequestURL'
    REQUEST_HEADER = 'RequestHeader'
    REQUEST_BODY = 'RequestBody'
    RESPONSE_HEADER = 'ResponseHeader'
    RESPONSE_BODY = 'ResponseBody'


def extract_token(location: str, rx: str, index: int | None, requests: list) -> str:
    if location not in ExchangeLocation.__members__.values():
        raise AuthenticationError(
            f'Invalid location `{location}`, must be one of: {" ,".join(ExchangeLocation.__members__.values())}',
        )

    tks = []
    if location == ExchangeLocation.REQUEST_URL:
        tks = extract_from_request_url(requests, rx)
    elif location == ExchangeLocation.REQUEST_HEADER:
        tks = extract_from_request_header(requests, rx)
    elif location == ExchangeLocation.REQUEST_BODY:
        tks = extract_from_request_body(requests, rx)
    elif location == ExchangeLocation.RESPONSE_HEADER:
        tks = extract_from_response_header(requests, rx)
    elif location == ExchangeLocation.RESPONSE_BODY:
        tks = extract_from_response_body(requests, rx)

    if not tks:
        raise AuthenticationError(
            f'All commands were executed but no token matching `{rx}` in `{location}` was found.',
        )

    index = index or 0
    logger.info(f'Found {len(tks)} tokens in `{location}` with regex `{rx}`. Taking index `{index}`')

    return tks[index]
