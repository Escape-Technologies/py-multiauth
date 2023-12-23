from http import HTTPMethod
from typing import Any

from pydantic import BaseModel, Field

from multiauth.entities.http import HTTPCookies, HTTPHeaders, HTTPLocation
from multiauth.entities.user import UserName

##### Authentications ######


class AuthRequester(BaseModel):
    url: str
    method: HTTPMethod
    body: Any | None
    headers: HTTPHeaders
    cookies: HTTPCookies


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


##### Credentials ####


class Credentials(BaseModel):
    name: UserName
    body: Any | None = Field(default=None)
    headers: HTTPHeaders = Field(default=HTTPHeaders({}))
    cookies: HTTPCookies = Field(default=HTTPCookies({}))


###### CONFIG ######


class AuthConfig(BaseModel):
    users: list[Credentials]
    methods: list[AuthProvider]
