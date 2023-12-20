"""Custom types of authentication module."""

from enum import Enum, unique
from typing import (
    Any,
    TypedDict,
    Union,
)

from attr import dataclass

from multiauth.entities.http import HTTPMethod
from multiauth.entities.providers.aws import AuthAWSType
from multiauth.entities.providers.http import HTTPLocation
from multiauth.entities.providers.oauth import AuthOAuthGrantType
from multiauth.entities.providers.webdriver import SeleniumProject


@unique
class AuthHashAlgorithmDigest(str, Enum):

    """The Available Hashing algorithms for Digest Authentication."""

    MD5 = 'md5'
    MD5_SESS = 'md5-sess'
    SHA_256 = 'sha-256'
    SHA_256_SESS = 'sha-256-sess'
    SHA_512_256 = 'sha-512-256'
    SHA_512_256_SESS = 'sha-512-256-sess'


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


class AuthDigestChallenge(TypedDict):

    """The format of the challenge in a digest authentication schema as specified by the RFC 2617."""

    realm: str | None
    domain: str | None
    nonce: str | None
    opaque: str | None
    algorithm: AuthHashAlgorithmDigest | None
    qop_options: str | None


class AuthConfigApiKey(TypedDict):

    """Authentication Configuration Parameters of the Api Key Method."""

    param_location: HTTPLocation
    param_name: str
    param_prefix: str | None
    headers: dict[str, str] | None


@dataclass
class WebdriverConfig:

    """Authentication Configuration Parameters of the Webdriver Method."""

    extract_location: str
    extract_regex: str
    project: SeleniumProject
    output_format: str
    token_lifetime: int | None
    extract_match_index: int | None


class AuthConfigDigest(TypedDict):

    """Authentication Configuration Parameters of the Digest Method."""

    url: str
    realm: str
    nonce: str
    algorithm: AuthHashAlgorithmDigest
    domain: str
    method: HTTPMethod
    qop: str | None
    nonce_count: str | None
    client_nonce: str | None
    opaque: str | None
    headers: dict[str, str] | None


class AuthResponse(TypedDict):

    """The Processed Authentication Configuration."""

    tech: AuthTech
    headers: dict[str, str]


Token = str


class RCFile(TypedDict):

    """RC File."""

    methods: dict
    users: dict


class JWTToken(TypedDict):

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
AuthType = Union[AuthAWSType, AuthOAuthGrantType]
