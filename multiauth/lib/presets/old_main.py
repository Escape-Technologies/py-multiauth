from http import HTTPMethod
from typing import Any

from pydantic import BaseModel, Field

from multiauth.lib.http_core.entities import HTTPCookie, HTTPEncoding, HTTPHeader, HTTPLocation
from multiauth.lib.store.user import UserName

##### Authentications ######


class AuthRequester(BaseModel):
    """The template of the Authentication request."""

    url: str = Field(description='The URL to of the Authentication request.')
    method: HTTPMethod = Field(default=HTTPMethod.POST, description='The HTTP method of the Authentication request.')
    body: Any | None = Field(default=None, description='The body of the Authentication request.')
    encoding: HTTPEncoding = Field(
        default=HTTPEncoding.JSON,
        description='The encoding of the Authentication request body.',
    )
    headers: list[HTTPHeader] = Field(
        default_factory=list,
        description='The mandatory headers of the Authentication request that are agnostic for every user.',
    )
    cookies: list[HTTPCookie] = Field(
        default_factory=list,
        description='The mandatory cookies of the Authentication request that are agnostic for every user.',
    )


class AuthExtractor(BaseModel):
    """How to extract the token from the response of the Authentication request."""

    location: HTTPLocation = Field(description='The location of the token in the response.')
    key: str = Field(default='token', description='The key of the token in the response.')


class AuthInjector(BaseModel):
    """How to inject the token into the authentified requests."""

    location: HTTPLocation = Field(
        default=HTTPLocation.HEADER,
        description='The location in which the token will be injected.',
    )
    key: str = Field(default='Authorization', description='The key in which the token will be injected.')
    prefix: str = Field(description='The prefix concatenated to the token when injected.')
    encoding: HTTPEncoding = Field(
        default=HTTPEncoding.JSON,
        description='The encoding of the token when injected into the body.',
    )


class AuthRefresher(BaseModel):
    requester: AuthRequester
    extractor: AuthExtractor
    injector: AuthInjector


class AuthProvider(BaseModel):
    requester: AuthRequester | None = Field(default=None)
    extractor: AuthExtractor | None = Field(default=None)
    injector: AuthInjector | None = Field(default=None)
    refresher: AuthRefresher | None = Field(default=None)


##### Credentials ####


class Credentials(BaseModel):
    """The credentials of a user."""

    name: UserName = Field(description='The arbitrary name given of the user.')
    body: Any | None = Field(default=None, description='The user-specific body of the Authentication request.')
    headers: list[HTTPHeader] = Field(default_factory=list, description='The user-specific headers.')
    cookies: list[HTTPCookie] = Field(default_factory=list, description='The user-specific cookies.')


###### CONFIG ######


class AuthConfig(BaseModel):
    users: list[Credentials]
    methods: list[AuthProvider]
