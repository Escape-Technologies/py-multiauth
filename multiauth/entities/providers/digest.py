"""Custom types of authentication module."""

from enum import StrEnum, unique
from http import HTTPMethod

from pydantic import BaseModel


@unique
class AuthHashAlgorithmDigest(StrEnum):

    """The Available Hashing algorithms for Digest Authentication."""

    MD5 = 'md5'
    MD5_SESS = 'md5-sess'
    SHA_256 = 'sha-256'
    SHA_256_SESS = 'sha-256-sess'
    SHA_512_256 = 'sha-512-256'
    SHA_512_256_SESS = 'sha-512-256-sess'


class AuthDigestChallenge(BaseModel):

    """The format of the challenge in a digest authentication schema as specified by the RFC 2617."""

    realm: str | None
    domain: str | None
    nonce: str | None
    opaque: str | None
    algorithm: AuthHashAlgorithmDigest | None
    qop_options: str | None


class AuthConfigDigest(BaseModel):

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
