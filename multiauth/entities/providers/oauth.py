"""Oauth provider."""

import sys
from enum import Enum, unique
from typing import Dict, Optional

from multiauth.entities.http import Location

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


@unique
class AuthOAuthlocation(str, Enum):

    """Where the credentials during the OAuth will be sent."""

    BASIC = 'basic'
    BODY = 'body'


@unique
class AuthOAuthGrantType(str, Enum):

    """The grant types of the OAuth."""

    AUTH_CODE = 'auth_code'
    CLIENT_CRED = 'client_cred'
    IMPLICIT = 'implicit'
    PASSWORD_CRED = 'password_cred'
    REFRESH_TOKEN = 'refresh_token'


# class AuthHashAlgorithmOAuth(Enum):

#     """The Available Hashing algorithm for OAuth authentication."""
#     PLAIN = 'plain'
#     SHA_256 = 'sha-256'


class AuthOAuthResponse(TypedDict):

    """The format of the OAuth access token response according to the official documentation."""

    access_token: str
    expires_in: Optional[float]
    refresh_token: Optional[str]


class AuthConfigOAuth(TypedDict):

    """Authentication Configuration Parameters of the OAuth Method."""

    grant_type: AuthOAuthGrantType
    authentication_endpoint: Optional[str]
    token_endpoint: Optional[str]
    callback_url: Optional[str]
    scope: str
    header_prefix: str
    auth_location: AuthOAuthlocation
    location: Location
    state: Optional[str]
    # challenge_method: Optional[AuthHashAlgorithmOAuth]
    code_verifier: Optional[str]
    headers: Optional[Dict[str, str]]
