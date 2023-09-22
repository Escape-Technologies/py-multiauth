"""Aws provider."""

import sys
from enum import Enum, unique
from typing import Dict, Optional

from multiauth.entities.http import HTTPMethod, Location

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


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
    user: Optional[str]
    nonce: Optional[str]
    ext: Optional[str]
    app: Optional[str]
    dig: Optional[str]
    timestamp: Optional[str]


class AuthConfigAWS(TypedDict):

    """Authenticaiton Configuration Parameters of the AWS Method."""

    type: AuthAWSType
    region: str
    client_id: Optional[str]
    method: Optional[HTTPMethod]
    service_name: Optional[str]
    hash_algorithm: Optional[AuthHashalgorithmHawkandAWS]
    pool_id: Optional[str]
    client_secret: Optional[str]
    location: Location
    header_name: Optional[str]
    header_prefix: Optional[str]
    headers: Optional[Dict[str, str]]
