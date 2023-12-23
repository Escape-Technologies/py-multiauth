from http import HTTPMethod
from typing import Any, NewType

from pydantic import Field

from multiauth.entities.http import HTTPCookies, HTTPHeaders, HTTPLocation
from multiauth.entities.user import UserName
from multiauth.new.entities.main import (
    AuthExtractor,
    AuthInjector,
    AuthProvider,
    AuthRefresher,
    AuthRequester,
    Credentials,
)

GraphQLQuery = NewType('GraphQLQuery', str)


class GraphQLAuthRequester(AuthRequester):
    url: str
    query: GraphQLQuery
    method: HTTPMethod = Field(default=HTTPMethod.POST)
    body: Any | None = Field(default=None)
    headers: HTTPHeaders = Field(default=HTTPHeaders({}))
    cookies: HTTPCookies = Field(default=HTTPCookies({}))


class GraphQLAuthExtractor(AuthExtractor):
    location: HTTPLocation = Field(default=HTTPLocation.BODY)
    key: str


class GraphQLAuthInjector(AuthInjector):
    key: str = Field(default='Authorization')
    location: HTTPLocation = Field(default=HTTPLocation.HEADER)
    prefix: str = Field(default='Bearer')


class AuthProviderGraphQL(AuthProvider):
    requester: GraphQLAuthRequester
    injector: GraphQLAuthInjector
    extractor: GraphQLAuthExtractor
    refresher: AuthRefresher | None = Field(default=None)


class GraphQLCredentials(Credentials):
    name: UserName
    body: Any | None = Field(default=None)
    headers: HTTPHeaders = Field(default=HTTPHeaders({}))
    cookies: HTTPCookies = Field(default=HTTPCookies({}))
    variables: dict[str, str]
