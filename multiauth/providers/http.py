"""Implementation of the Rest authentication schema."""

from typing import Dict

from multiauth.entities.errors import AuthenticationError
from multiauth.entities.main import AuthResponse, AuthTech
from multiauth.entities.providers.http import (
    AuthProvider,
)
from multiauth.manager import User
from multiauth.providers.http_parser import parse_config


def attach_auth(
    user: User,
    auth_config: AuthProvider,
    proxy: str | None = None,
) -> AuthResponse:
    """This function takes the credentials of the user and authenticates them on the authentication URL."""

    if user and auth_config and proxy:  # TODO(antoine@escape.tech): remove this and code the function
        raise AuthenticationError('Cannot use proxy with user credentials')

    return AuthResponse(tech=AuthTech.REST, headers={})


def http_authenticator(
    user: User,
    schema: Dict,
    proxy: str | None = None,
) -> AuthResponse:
    """This funciton is a wrapper function that implements the Rest authentication schema.

    It takes the credentials of the user and authenticates them on the authentication URL.
    After authenticating, it fetches the token and adds the token to the
    headers along with optional headers in case the user provided them.
    """

    auth_config = parse_config(schema)
    return attach_auth(user, auth_config, proxy=proxy)
