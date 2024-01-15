import json
from os import getenv
from urllib.parse import urlencode, urlunparse

import httpx

from multiauth.lib.audit.events.events import HTTPFailureEvent
from multiauth.lib.http_core.entities import (
    HTTPCookie,
    HTTPHeader,
    HTTPRequest,
    HTTPResponse,
)

HTTP_REQUEST_TIMEOUT = 5


def _request(
    method: str,
    url: str,
    headers: dict[str, str],
    cookies: dict[str, str],
    data: str | None = None,
    timeout: int | None = None,
    proxy: str | None = None,
) -> httpx.Response:
    ca_bundle = getenv('REQUESTS_CA_BUNDLE', '')
    context = httpx.create_ssl_context(verify=ca_bundle if ca_bundle else True)

    with httpx.Client(
        http2=True,
        trust_env=False,
        proxies=proxy,
        verify=context,
    ) as client:
        return client.request(
            method=method,
            url=url,
            headers=headers,
            cookies=cookies,
            content=data,
            timeout=timeout or 5,
        )


def send_request(request: HTTPRequest) -> HTTPResponse | HTTPFailureEvent:
    """Send HTTP request."""

    query_parameters = {qp.name: qp.values for qp in request.query_parameters}
    headers = {h.name: ','.join(h.values) for h in request.headers}
    cookies = {c.name: ','.join(c.values) for c in request.cookies}

    url = urlunparse((request.scheme.value, request.host, request.path, '', urlencode(query_parameters), ''))

    try:
        response = _request(
            method=request.method.value,
            url=url,
            headers=headers,
            cookies=cookies,
            data=request.data_text,
            timeout=HTTP_REQUEST_TIMEOUT,
            proxy=request.proxy,
        )
    except httpx.TimeoutException as e:
        return HTTPFailureEvent(reason='timeout', description=str(e))
    except httpx.ConnectError as e:
        return HTTPFailureEvent(reason='connection_error', description=str(e))
    except httpx.TooManyRedirects as e:
        return HTTPFailureEvent(reason='too_many_redirects', description=str(e))
    except httpx.HTTPError as e:
        return HTTPFailureEvent(reason='unknown', description=str(e))
    except Exception as e:
        return HTTPFailureEvent(reason='unknown', description=str(e))

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
        url=url,
        status_code=response.status_code,
        reason=response.reason_phrase,
        headers=response_headers,
        cookies=response_cookies,
        data_text=response.text,
        data_json=data_json,
        elapsed=response.elapsed,
    )
