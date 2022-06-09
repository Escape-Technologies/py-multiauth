"""Aws provider."""

from enum import Enum, unique
from typing import TypedDict

from multiauth.types.http import HTTPMethod, Location


@unique
class AuthAWSType(str, Enum):

    """The authentication flow used in the AWS authentication."""
    USER_SRP_AUTH = 'SRP'
    USER_PASSWORD_AUTH = 'Password Authentication'
    AWS_SIGNATURE = 'AWS Signature'
    REFRESH_TOKEN = 'refresh_token'


@unique
class AuthAWSChallengeResponse(str, Enum):

    """The types of challenge responses."""
    NEW_PASSWORD_REQUIRED_CHALLENGE = 'NEW_PASSWORD_REQUIRED'
    PASSWORD_VERIFIER_CHALLENGE = 'PASSWORD_VERIFIER'


@unique
class AuthHashalgorithmHawkandAWS(str, Enum):

    """The Available Hashing algorithm for Hawk authentication."""
    SHA_256 = 'sha-256'
    SHA_1 = 'sha-1'


class AuthConfigHawk(TypedDict):

    """Authentication Configuration Parameters of the Hawk Method."""
    algorithm: AuthHashalgorithmHawkandAWS
    user: str | None
    nonce: str | None
    ext: str | None
    app: str | None
    dig: str | None
    timestamp: str | None


class AuthConfigAWS(TypedDict):

    """Authenticaiton Configuration Parameters of the AWS Method."""
    type: AuthAWSType
    region: str
    client_id: str | None
    method: HTTPMethod | None
    service_name: str | None
    hash_algorithm: AuthHashalgorithmHawkandAWS | None
    pool_id: str | None
    client_secret: str | None
    location: Location
    header_name: str | None
    header_key: str | None
    headers: dict[str, str] | None
