import json
from urllib.parse import urlencode, urlunparse

import requests

from multiauth.lib.http_core.entities import (
    HTTPCookie,
    HTTPHeader,
    HTTPRequest,
    HTTPResponse,
)

HTTP_REQUEST_TIMEOUT = 5


def send_request(request: HTTPRequest) -> HTTPResponse:
    """Send HTTP request."""

    query_parameters = {qp.name: qp.values for qp in request.query_parameters}
    headers = {h.name: ','.join(h.values) for h in request.headers}
    cookies = {c.name: ','.join(c.values) for c in request.cookies}

    url = urlunparse((request.scheme.value, request.host, request.path, '', urlencode(query_parameters), ''))

    try:
        response = requests.request(
            request.method.value,
            url,
            headers=headers,
            cookies=cookies,
            data=request.data_text,
            timeout=HTTP_REQUEST_TIMEOUT,
            proxies={'http': request.proxy, 'https': request.proxy} if request.proxy else None,
            verify=False if request.proxy else None,
        )
    except requests.exceptions.HTTPError as e:
        response = e.response

    data_json = None
    try:
        data_json = response.json()
    except json.JSONDecodeError:
        pass

    response_headers: list[HTTPHeader] = [
        HTTPHeader(name=name, values=list(value.split(','))) for name, value in response.headers.items()
    ]

    response_cookies: list[HTTPCookie] = [
        HTTPCookie(name=name, values=list(value.split(','))) for name, value in dict(response.cookies).items()
    ]

    return HTTPResponse(
        url=response.url,
        status_code=response.status_code,
        reason=response.reason,
        headers=response_headers,
        cookies=response_cookies,
        data_text=response.text,
        data_json=data_json,
        elapsed=response.elapsed,
    )
