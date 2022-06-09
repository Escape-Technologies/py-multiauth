"""Custom types of authentication module."""

from enum import Enum, unique
from typing import Any, TypedDict

from multiauth.types.http import HTTPMethod, Location
from multiauth.types.providers.aws import AuthAWSType
from multiauth.types.providers.oauth import AuthOAuthGrantType


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
    NOAUTH = 'noauth'
    OAUTH = 'oauth'


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
    location: Location
    header_name: str
    header_prefix: str | None
    headers: dict[str, str] | None


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


class JWTToken(TypedDict):

    """This class finds all the registered claims in the JWT token payload."""

    # Signature algorithm
    sig: str

    # Identifies who isssued the JWT token
    iss: str | None

    # Identifies who the token is refered to
    sub: str | None

    # Identitfies who the token is intended for
    aud: str | None

    # Expiration Time
    exp: str | None

    # Identifies the time before which the JWT token must not be accepted
    nbf: str | None

    # Issued Time
    iat: str | None

    # JWT ID
    jti: str | None

    # Custom Names
    other: dict[Any, Any]


# Helper Entities

AuthType = AuthAWSType | AuthOAuthGrantType
