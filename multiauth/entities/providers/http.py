from http import HTTPMethod
from typing import Any

from pydantic import BaseModel

from multiauth.entities.http import HTTPLocation

##### Authentications ######


class AuthRequester(BaseModel):
    url: str
    method: HTTPMethod
    body: Any | None
    headers: dict[str, str]
    cookies: dict[str, str]


class AuthExtractor(BaseModel):
    location: HTTPLocation
    key: str  # this is use to extract the token from the response in depth in the location


class AuthInjector(BaseModel):
    key: str
    location: HTTPLocation
    prefix: str


class AuthRefresher(BaseModel):
    requester: AuthRequester
    extractor: AuthExtractor
    injector: AuthInjector


class AuthProvider(BaseModel):
    requester: AuthRequester
    extractor: AuthExtractor
    injector: AuthInjector
    refresher: AuthRefresher | None


###### Authentication Extensions ######


class GraphQLAuthRequester(AuthRequester):
    query: str


##### Credentials ####


class Credentials(BaseModel):
    name: str
    body: Any | None
    headers: dict[str, str]
    cookies: dict[str, str]


class RESTCredentials(Credentials):
    pass


class APICredentials(Credentials):
    pass


class BasicCredentials(Credentials):
    username: str
    password: str


class GraphQLCredentials(Credentials):
    variables: dict[str, str]
