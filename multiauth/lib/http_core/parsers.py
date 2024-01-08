from http import HTTPMethod
from typing import Any
from urllib.parse import urlparse

from multiauth.lib.http_core.entities import HTTPScheme


def parse_method(raw_method: Any) -> HTTPMethod:
    if not isinstance(raw_method, str):
        raise ValueError('Provided method is not cURL command with a valid method.')
    if not raw_method:
        return HTTPMethod.GET
    raw_method = raw_method.upper()
    try:
        return HTTPMethod(raw_method)
    except ValueError as e:
        raise ValueError(
            f'Invalid method {raw_method.upper()}',
        ) from e


def parse_scheme(raw_scheme: Any) -> HTTPScheme:
    if not raw_scheme or not isinstance(raw_scheme, str):
        raise ValueError('Provided scheme is not set or not a string. Valid schemes are "http" and "https"')
    scheme = raw_scheme.lower()
    if scheme == HTTPScheme.HTTP.value:
        return HTTPScheme.HTTP
    if scheme == HTTPScheme.HTTPS.value:
        return HTTPScheme.HTTPS
    raise ValueError('Input is not cURL command with a valid scheme. Valid schemes are "http" and "https"')


def parse_raw_url(raw_url: Any) -> tuple[HTTPScheme, str, str]:
    if not raw_url.startswith('http://') and not raw_url.startswith('https://'):
        raw_url = 'http://' + raw_url
    url = urlparse(raw_url)

    return parse_scheme(url.scheme), url.netloc, url.path or '/'
