"""Multiauth types related to HTTP protocol."""
import datetime
import enum
import json
from http import HTTPMethod
from urllib.parse import quote, urlparse, urlunparse

from pydantic import Field, field_serializer

from multiauth.helpers.base_model import StrictBaseModel

JSONSerializable = dict | list | str | int | float | bool


class HTTPEncoding(enum.StrEnum):
    """The MIME encoding of the HTTP request body."""

    JSON = 'application/json'
    FORM = 'application/x-www-form-urlencoded'
    TEXT = 'text/plain'
    XML = 'application/xml'
    HTML = 'text/html'
    MULTIPART = 'multipart/form-data'
    YAML = 'application/x-yaml'
    CSV = 'text/csv'
    BINARY = 'application/octet-stream'
    AWS_JSON = 'application/x-amz-json-1.1'


class HTTPLocation(enum.StrEnum):
    HEADER = 'header'
    COOKIE = 'cookie'
    BODY = 'body'
    QUERY = 'query'


class HTTPScheme(enum.StrEnum):
    HTTP = 'http'
    HTTPS = 'https'


class HTTPHeader(StrictBaseModel):
    name: str
    values: list[str]

    @property
    def str_value(self) -> str:
        return ','.join(self.values)


class HTTPCookie(StrictBaseModel):
    name: str
    values: list[str]

    @property
    def str_value(self) -> str:
        return quote(','.join(self.values))

    @staticmethod
    def serialize(cookies: list['HTTPCookie']) -> str:
        return '; '.join(f'{cookie.name}={cookie.str_value}' for cookie in cookies)


class HTTPQueryParameter(StrictBaseModel):
    name: str
    values: list[str]

    @property
    def str_value(self) -> str:
        return quote(','.join(self.values))


class HTTPRequest(StrictBaseModel):
    method: HTTPMethod
    host: str
    scheme: HTTPScheme
    path: str
    headers: list[HTTPHeader] = Field(default_factory=list)
    username: str | None = Field(default=None)
    password: str | None = Field(default=None)
    data_json: JSONSerializable | None = Field(default=None)
    data_text: str | None = Field(default=None)
    query_parameters: list[HTTPQueryParameter] = Field(default_factory=list)
    cookies: list[HTTPCookie] = Field(default_factory=list)
    proxy: str | None = Field(default=None)
    timeout: int = Field(default=5)

    def __to_http_document(self) -> str:
        scheme_str = 'HTTP/1.1' if self.scheme.value == 'http' else 'HTTPS/1.1'
        document = f'{self.method} {self.path} {scheme_str}\n'

        headers = [*self.headers, HTTPHeader(name='Host', values=[self.host])]
        if len(self.cookies) > 0:
            cookie_header = HTTPHeader(
                name='Cookie',
                values=[f'{cookie.name}={cookie.str_value}' for cookie in self.cookies],
            )
            headers = [*headers, cookie_header]

        for header in headers:
            document += f'{header.name}: {",".join(header.values)}\n'

        if self.data_json is not None:
            document += '\n'
            document += json.dumps(self.data_json, indent=4)
            document += '\n'

        elif self.data_text is not None and self.data_text != '':
            document += '\n'
            document += self.data_text
            document += '\n'

        return document

    @staticmethod
    def from_url(url: str) -> 'HTTPRequest':
        parsed_url = urlparse(url)
        return HTTPRequest(
            method=HTTPMethod.GET,
            host=parsed_url.netloc,
            path=parsed_url.path,
            scheme=HTTPScheme(parsed_url.scheme),
        )

    @property
    def url(self) -> str:
        return urlunparse((self.scheme.value, self.host, self.path, '', '', ''))


class HTTPResponse(StrictBaseModel):
    url: str
    status_code: int
    reason: str
    elapsed: datetime.timedelta
    headers: list[HTTPHeader] = Field(default_factory=list)
    cookies: list[HTTPCookie] = Field(default_factory=list)
    data_text: str | None = Field(default=None)
    data_json: JSONSerializable | None = Field(default=None)

    @field_serializer('elapsed')
    def serialize_elapsed(self, elapsed: datetime.timedelta) -> float:
        return elapsed.total_seconds()

    def __to_http_document(self) -> str:
        document = f'{self.status_code} {self.reason} ({self.elapsed}s)\n'

        headers = self.headers
        if len(self.cookies) > 0:
            cookie_header = HTTPHeader(
                name='Cookie',
                values=[f'{cookie.name}={cookie.str_value}' for cookie in self.cookies],
            )
            headers = [*headers, cookie_header]

        for header in headers:
            document += f'{header.name}: {",".join(header.values)}\n'

        if self.data_json is not None:
            document += '\n'
            document += json.dumps(self.data_json, indent=2)
            document += '\n'

        elif self.data_text is not None and self.data_text != '':
            document += '\n'
            document += self.data_text
            document += '\n'

        return document
