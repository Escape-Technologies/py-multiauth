"""Multiauth types related to HTTP protocol."""
import datetime
import enum
from http import HTTPMethod
from typing import Any

from pydantic import BaseModel


class HTTPLocation(enum.StrEnum):
    HEADER = 'header'
    COOKIE = 'cookie'
    BODY = 'body'
    QUERY = 'query'


class HTTPScheme(enum.StrEnum):
    HTTP = 'http'
    HTTPS = 'https'

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


JSONSerializable = dict | list | str | int | float | bool


class HTTPRequest(BaseModel):
    method: HTTPMethod
    host: str
    scheme: HTTPScheme
    path: str
    headers: dict[str, str]
    username: str | None
    password: str | None
    data_json: JSONSerializable | None
    data_text: str | None
    query_parameters: dict[str, list[str]]
    cookies: dict[str, str]
    proxy: str | None
    timeout: int = 5


class HTTPResponse(BaseModel):
    url: str
    status_code: int
    reason: str
    headers: dict[str, str]
    cookies: dict[str, str]
    data_text: str | None
    data_json: JSONSerializable | None
    elapsed: datetime.timedelta
