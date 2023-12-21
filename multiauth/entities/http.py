"""Multiauth types related to HTTP protocol."""
import datetime
import enum
from http import HTTPMethod

from pydantic import BaseModel


class HTTPLocation(enum.StrEnum):
    HEADER = 'header'
    COOKIE = 'cookie'
    BODY = 'body'
    QUERY = 'query'


class HTTPScheme(enum.StrEnum):
    HTTP = 'http'
    HTTPS = 'https'


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
