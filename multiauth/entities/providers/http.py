from http import HTTPMethod
from typing import Any, NewType

from pydantic import BaseModel

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


###### Authentication Extensions ######


GraphQLQuery = NewType('GraphQLQuery', str)


class GraphQLAuthRequester(AuthRequester):
    query: GraphQLQuery


##### AuthenticatinMethods ####


##### Credentials ####


class Credentials(BaseModel):
    name: UserName
    body: Any | None
    headers: HTTPHeaders
    cookies: HTTPCookies


class RESTCredentials(BaseModel):
    pass


class BasicCredentials(Credentials):
    username: str
    password: str


class GraphQLCredentials(Credentials):
    variables: dict[str, str]


class DigestCredentials(Credentials):
    username: str
    password: str


class AWSRefreshCredentials(Credentials):
    refreshToken: str


class AWSSignatureCredentials(Credentials):
    accessKey: str
    secretKey: str


class AWSPasswordCredentials(Credentials):
    username: str
    password: str


class AWSSRPCredentials(Credentials):
    username: str
    password: str


class OAuth2AuthCodeCredentials(Credentials):
    clientId: str
    clientSecret: str


class OAuth2ClientCredentials(Credentials):
    clientId: str
    clientSecret: str


class OAuth2PasswordCredentials(Credentials):
    clientId: str
    clientSecret: str
    username: str
    password: str


class OAuth2ImplicitCredentials(Credentials):
    clientId: str


###### CONFIG ######


class AuthConfig(BaseModel):
    users: list[Credentials]
    methods: list[AuthProvider]
