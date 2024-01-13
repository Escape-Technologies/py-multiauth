import logging
import re
from typing import Any, Literal

from seleniumwire.request import Request  # type: ignore[import-untyped]

from multiauth.lib.http_core.entities import HTTPLocation

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
    location: HTTPLocation,
    key: str,  # noqa: ARG001 todo(antoine@escape.tech): Uniformise extraction
    regex: str | None,
    requests: list[Request],
) -> str:
    if regex is None:
        raise Exception('Regex is required')

    match location:
        case HTTPLocation.BODY:
            tokens = extract_from_request_body(requests, regex)
            tokens += extract_from_response_body(requests, regex)
        case HTTPLocation.HEADER:
            tokens = extract_from_request_header(requests, regex)
            tokens += extract_from_response_header(requests, regex)
        case HTTPLocation.QUERY:
            tokens = extract_from_request_url(requests, regex)

    _l = len(tokens)

    if _l == 0:
        raise Exception(f'Could not find token in `{location}` with regex `{regex}`')

    if _l > 1:
        raise Exception(
            f'We could find {_l} token in `{location}` with regex `{regex}`: `{tokens}`.\
              Please strengthen your regex so that only one is found.',
        )

    return tokens[0]
