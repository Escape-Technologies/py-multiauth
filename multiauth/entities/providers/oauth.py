"""Oauth provider."""

from enum import Enum, unique
from typing import (
    TypedDict,
)

from multiauth.entities.providers.http import HTTPLocation
from multiauth.entities.providers.webdriver import SeleniumCommand


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
    expires_in: float | None
    refresh_token: str | None


class AuthConfigOAuth(TypedDict):

    """Authentication Configuration Parameters of the OAuth Method."""

    grant_type: AuthOAuthGrantType
    authentication_endpoint: str | None
    token_endpoint: str | None
    callback_url: str | None
    scope: str | None
    param_prefix: str
    auth_location: AuthOAuthlocation
    param_location: HTTPLocation
    state: str | None
    login_flow: list[SeleniumCommand]
    # challenge_method: AuthHashAlgorithmOAuth | None
    code_verifier: str | None
    headers: dict[str, str] | None
