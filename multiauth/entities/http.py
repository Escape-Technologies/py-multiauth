"""Multiauth types related to HTTP protocol."""
import datetime
import enum
from dataclasses import dataclass
from http import HTTPMethod


class HTTPLocation(enum.StrEnum):
    HEADER = 'header'
    COOKIE = 'cookie'
    BODY = 'body'
    QUERY = 'query'


class HTTPScheme(enum.StrEnum):
    HTTP = 'http'
    HTTPS = 'https'


JSONSerializable = dict | list | str | int | float | bool | None


@dataclass
class HTTPRequest:
    method: HTTPMethod
    host: str
    scheme: HTTPScheme
    path: str
    headers: dict[str, str]
    username: str | None
    password: str | None
    json: JSONSerializable | None
    data: str | None
    query_parameters: dict[str, list[str]]
    cookies: dict[str, str]
    proxy: str | None
    timeout: int = 5


@dataclass
class HTTPResponse:
    url: str
    status_code: int
    reason: str
    headers: dict[str, str]
    cookies: dict[str, str]
    data: str | None
    json: JSONSerializable | None
    elapsed: datetime.timedelta
