"""Custom types of authentication module."""

from enum import StrEnum, unique
from typing import (
    Any,
    NewType,
)

from pydantic import BaseModel, Field

from multiauth.entities.http import HTTPCookies, HTTPHeaders
from multiauth.entities.providers.http import Credentials


# The Authentication Schemas can be found below
@unique
class AuthTech(StrEnum):

    """Authentication Method Enumeration."""

    APIKEY = 'api_key'
    AWS = 'aws'
    BASIC = 'basic'
    REST = 'rest'
    DIGEST = 'digest'
    GRAPHQL = 'graphql'
    HAWK = 'hawk'
    MANUAL = 'manual'
    PUBLIC = 'public'
    OAUTH = 'oauth'
    WEBDRIVER = 'webdriver'


class AuthResponse(Credentials):

    """The Processed Authentication Configuration."""

    cookies: HTTPCookies = Field(default=HTTPCookies({}))
    headers: HTTPHeaders = Field(default=HTTPHeaders({}))
    body: Any = Field(default=None)
    tech: AuthTech


Token = NewType('Token', str)


class RCFile(BaseModel):

    """RC File."""

    methods: dict
    users: dict


class JWTToken(BaseModel):

    """This class finds all the registered claims in the JWT token payload.

    Attributes:
        sig: Signature algorthm used in the JWT token.
        iss: Issuer of the JWT token.
        sub: Subject of the JWT token.
        aud: Audience of the JWT token -> intended for.
        exp: Expiration time of the JWT token.
        nbf: Identifies the time before which the JWT token is not yet valid.
        iat: Issued at time of the JWT token.
        jti: JWT token identifier.
        other: Other claims in the JWT token.
    """

    sig: str
    iss: str | None
    sub: str | None
    aud: str | None
    exp: int | None
    nbf: int | None
    iat: int | None
    jti: str | None
    other: dict[Any, Any]
