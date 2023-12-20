from dataclasses import dataclass
from http import HTTPMethod
from typing import Any

from multiauth.entities.http import HTTPLocation

##### Authentications ######


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
    key: str
    location: HTTPLocation
    prefix: str


@dataclass
class AuthRefresher:
    requester: AuthRequester
    extractor: AuthExtractor
    injector: AuthInjector


@dataclass
class AuthProvider:
    requester: AuthRequester
    extractor: AuthExtractor
    injector: AuthInjector
    refresher: AuthRefresher | None


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
