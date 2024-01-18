import re
from typing import Literal

from seleniumwire.request import HTTPHeaders, Request  # type: ignore  # noqa: PGH003

from multiauth.lib.http_core.entities import HTTPLocation

WebdriverTokenLocationType = Literal['RequestURL', 'RequestHeader', 'RequestBody', 'ResponseHeader', 'ResponseBody']


def extract_from_request_url(url: str, rx: str) -> list[str]:
    res = []

    if match := re.search(rx, url):
        res.append(match.group(1))

    return res


def extract_from_header(headers: HTTPHeaders, rx: str) -> list[str]:
    res = []

    for header, header_value in headers.items():
        if match := re.search(rx, header + ': ' + header_value):
            res.append(match.group(1))

    return res


def extract_from_body(body: bytes, rx: str) -> list[str]:
    res = []
    if match := re.search(rx, body.decode()):
        res.append(match.group(1))

    return res


def extract_token(
    location: HTTPLocation,
    key: str,  # noqa: ARG001 todo(antoine@escape.tech): Uniformise extraction
    regex: str | None,
    requests: list[Request],
) -> str:
    if regex is None:
        raise Exception('Regex is required')

    tokens: list[str] = []

    match location:
        case HTTPLocation.BODY:
            for request in requests:
                if request.body:
                    tokens += extract_from_body(request.body, regex)
                if request.response and request.response.body:
                    tokens += extract_from_body(request.response.body, regex)
        case HTTPLocation.HEADER:
            for request in requests:
                tokens += extract_from_header(request.headers, regex)
                if request.response:
                    tokens += extract_from_header(request.response.headers, regex)
        case HTTPLocation.QUERY:
            urls = [request.url for request in requests]
            for url in urls:
                tokens += extract_from_request_url(url, regex)

    _l = len(tokens)

    if _l == 0:
        raise Exception(f'Could not find token in `{location}` with regex `{regex}`')

    if _l > 1:
        raise Exception(
            f'We could find {_l} token in `{location}` with regex `{regex}`: `{tokens}`.\
              Please strengthen your regex so that only one is found.',
        )

    return tokens[0]
