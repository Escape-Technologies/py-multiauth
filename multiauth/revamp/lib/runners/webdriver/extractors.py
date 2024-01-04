import logging
import re
from typing import Any, Literal

from seleniumwire.request import Request  # type: ignore[import-untyped]

WebdriverTokenLocationType = Literal['RequestURL', 'RequestHeader', 'RequestBody', 'ResponseHeader', 'ResponseBody']

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


def extract_token(
    location: WebdriverTokenLocationType,
    regex: str,
    index: int | None,
    requests: list[Request],
) -> str:
    match location:
        case 'RequestBody':
            tokens = extract_from_request_body(requests, regex)
        case 'RequestHeader':
            tokens = extract_from_request_header(requests, regex)
        case 'RequestURL':
            tokens = extract_from_request_url(requests, regex)
        case 'ResponseBody':
            tokens = extract_from_response_body(requests, regex)
        case 'ResponseHeader':
            tokens = extract_from_response_header(requests, regex)

    if len(tokens) == 0:
        raise Exception(f'Could not find token in `{location}` with regex `{regex}`')

    index = index or 0
    if len(tokens) <= index:
        raise Exception(f'Could not find token in `{location}` with regex `{regex}` at index `{index}`')

    return tokens[index]
