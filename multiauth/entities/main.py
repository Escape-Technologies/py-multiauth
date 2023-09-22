"""Custom types of authentication module."""

import sys
from enum import Enum, unique
from typing import Any, Dict, Optional, Union

from attr import dataclass

from multiauth.entities.http import HTTPMethod, Location
from multiauth.entities.providers.aws import AuthAWSType
from multiauth.entities.providers.oauth import AuthOAuthGrantType

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


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

    realm: Optional[str]
    domain: Optional[str]
    nonce: Optional[str]
    opaque: Optional[str]
    algorithm: Optional[AuthHashAlgorithmDigest]
    qop_options: Optional[str]


class AuthConfigApiKey(TypedDict):

    """Authentication Configuration Parameters of the Api Key Method."""

    location: Location
    header_name: str
    header_prefix: Optional[str]
    headers: Optional[Dict[str, str]]


@dataclass
class WebdriverConfig:

    """Authentication Configuration Parameters of the Webdriver Method."""

    extract_location: str
    extract_regex: str
    project: Dict[str, Any]
    output_format: Optional[str]
    token_lifetime: Optional[int]
    extract_match_index: Optional[int]


class AuthConfigDigest(TypedDict):

    """Authentication Configuration Parameters of the Digest Method."""

    url: str
    realm: str
    nonce: str
    algorithm: AuthHashAlgorithmDigest
    domain: str
    method: HTTPMethod
    qop: Optional[str]
    nonce_count: Optional[str]
    client_nonce: Optional[str]
    opaque: Optional[str]
    headers: Optional[Dict[str, str]]


class AuthResponse(TypedDict):

    """The Processed Authentication Configuration."""

    tech: AuthTech
    headers: Dict[str, str]


Token = str


class RCFile(TypedDict):

    """RC File."""

    auth: Dict
    users: Dict


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
    iss: Optional[str]
    sub: Optional[str]
    aud: Optional[str]
    exp: Optional[str]
    nbf: Optional[str]
    iat: Optional[str]
    jti: Optional[str]
    other: Dict[Any, Any]


# Helper Entities
AuthType = Union[AuthAWSType, AuthOAuthGrantType]
