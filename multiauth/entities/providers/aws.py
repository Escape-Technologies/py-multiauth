"""Aws provider."""

from enum import StrEnum, unique

from pydantic import BaseModel

from multiauth.entities.http import HTTPMethod
from multiauth.entities.providers.http import HTTPLocation


@unique
class AuthAWSType(StrEnum):

    """The authentication flow used in the AWS authentication."""

    USER_SRP_AUTH = 'SRP'
    USER_PASSWORD_AUTH = 'Password Authentication'
    AWS_SIGNATURE = 'AWS Signature'
    REFRESH_TOKEN = 'refresh_token'


@unique
class AuthAWSChallengeResponse(StrEnum):

    """The types of challenge responses."""

    NEW_PASSWORD_REQUIRED_CHALLENGE = 'NEW_PASSWORD_REQUIRED'
    PASSWORD_VERIFIER_CHALLENGE = 'PASSWORD_VERIFIER'


@unique
class AuthHashalgorithmHawkandAWS(StrEnum):

    """The Available Hashing algorithm for Hawk authentication."""

    SHA_256 = 'sha-256'
    SHA_1 = 'sha-1'


class AuthConfigAWS(BaseModel):

    """Authenticaiton Configuration Parameters of the AWS Method."""

    type: AuthAWSType
    region: str
    client_id: str | None
    method: HTTPMethod | None
    service_name: str | None
    hash_algorithm: AuthHashalgorithmHawkandAWS | None
    pool_id: str | None
    client_secret: str | None
    param_location: HTTPLocation
    param_name: str | None
    param_prefix: str | None
    headers: dict[str, str] | None
