import re
from typing import Any
import itertools

def extract_from_request_url(requests: Any, rx: re.Pattern) -> str | None:
    for request in requests:
        if match := re.search(rx, request.url):
            return match.group(1)

    return None

def extract_from_request_header(requests: Any, rx: re.Pattern) -> str | None:
    for header in itertools.chain.from_iterable(
        request.headers for request in requests
    ):
        if match := re.search(rx, header):
            return match.group(1)

    return None

def extract_from_response_header(requests: Any, rx: re.Pattern) -> str | None:
    for header in itertools.chain.from_iterable(
        request.response.headers for request in requests
        if request.response
    ):
        if match := re.search(rx, header):
            return match.group(1)

    return None

def extract_from_request_body(requests: Any, rx: re.Pattern) -> str | None:
    for request in requests:
        if match := re.search(rx, request.body):
            return match.group(1)

    return None

def extract_from_response_body(requests: Any, rx: re.Pattern) -> str | None:
    for request in requests:
        if match := re.search(rx, request.response.body):
            return match.group(1)

    return None
