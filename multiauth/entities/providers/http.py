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
class AuthRefresher:
    input: AuthRequester
    extract: AuthExtractor


@dataclass
class AuthProvider:
    input: AuthRequester
    extract: AuthExtractor
    inject: AuthInjector
    refresh: Optional['AuthProvider']


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
