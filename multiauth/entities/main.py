"""Custom types of authentication module."""

from dataclasses import dataclass
from enum import Enum, unique
from typing import (
    Any,
    TypedDict,
)

from multiauth.entities.providers.aws import AuthAWSType
from multiauth.entities.providers.oauth import AuthOAuthGrantType


# The Authentication Schemas can be found below
@unique
class AuthTech(str, Enum):

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


class AuthResponse(TypedDict):

    """The Processed Authentication Configuration."""

    tech: AuthTech
    headers: dict[str, str]


Token = str


@dataclass
class RCFile:

    """RC File."""

    methods: dict
    users: dict


@dataclass
class JWTToken:

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
    exp: str | None
    nbf: str | None
    iat: str | None
    jti: str | None
    other: dict[Any, Any]


# Helper Entities
AuthType = AuthAWSType | AuthOAuthGrantType
