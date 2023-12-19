import datetime
import enum
from dataclasses import dataclass
from http import HTTPMethod
from typing import Any, Optional

##### Authentications ######


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


@dataclass
class AuthRequester:
    url: str
    method: HTTPMethod
    body: Any | None
    headers: dict[str, str]
    cookies: dict[str, str]


@dataclass
class AuthExtractor:
    location: HTTPLocation
    key: str  # this is use to extract the token from the response in depth in the location


@dataclass
class AuthInjector:
    key: str | list[str]  # list[str] is used for in depth token injection in body
    location: HTTPLocation
    prefix: str


@dataclass
class AuthProvider:
    requester: AuthRequester
    extractor: AuthExtractor
    injector: AuthInjector
    refresher: Optional['AuthProvider']


###### Authentication Extensions ######


@dataclass
class GraphQLAuthRequester(AuthRequester):
    query: str


##### Credentials ####


@dataclass
class Credentials:
    name: str
    body: Any | None
    headers: dict[str, str]
    cookies: dict[str, str]


@dataclass
class RESTCredentials(Credentials):
    pass


@dataclass
class APICredentials(Credentials):
    pass


@dataclass
class BasicCredentials(Credentials):
    username: str
    password: str


@dataclass
class GraphQLCredentials(Credentials):
    variables: dict[str, str]
