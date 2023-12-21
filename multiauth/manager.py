"""User manager."""

import time
from typing import Any

from multiauth.entities.errors import AuthenticationError, ExpiredTokenError
from multiauth.entities.main import AuthTech, AuthType, JWTToken, Token
from multiauth.helpers import jwt_token_analyzer


class User:

    """User entity."""

    auth_schema: str | None
    auth_tech: AuthTech
    auth_type: AuthType | None
    credentials: dict[str, Any] | None
    expired_token: Token | None
    expires_in: int | None
    headers: dict[str, Any] | None
    refresh_token: Token | None
    token_info: JWTToken | None
    token: Token | None

    def __init__(
        self,
        auth_schema: str | None = None,
        auth_tech: AuthTech = AuthTech.PUBLIC,
        auth_type: AuthType | None = None,
        credentials: dict[str, Any] | None = None,
        expired_token: Token | None = None,
        expires_in: int | None = None,
        headers: dict[str, Any] | None = None,
        refresh_token: Token | None = None,
        token_info: JWTToken | None = None,
        token: Token | None = None,
    ) -> None:
        """Init user."""

        self.reset()

        self.auth_schema = auth_schema
        self.auth_tech = auth_tech
        self.auth_type = auth_type
        self.credentials = credentials
        self.token = token
        self.expired_token = expired_token
        self.expires_in = expires_in
        self.headers = headers
        self.refresh_token = refresh_token
        self.token_info = token_info
        self.token = token

        for token in [self.token, self.refresh_token]:
            if not token:
                continue

            serialized_token = jwt_token_analyzer(token)
            if serialized_token.exp is not None:
                self.expires_in = int(serialized_token.exp - time.time())
                if self.expires_in < 0:
                    raise ExpiredTokenError('Token expired.')

    def reset(self) -> None:
        """Reset user."""

        self.auth_schema = None
        self.auth_tech = AuthTech.PUBLIC
        self.auth_type = None
        self.credentials = None
        self.expired_token = None
        self.expires_in = None
        self.headers = None
        self.refresh_token = None
        self.token_info = None
        self.token = None

    def set_token(
        self,
        token: Token | None,
        expires_in: int | None,
    ) -> None:
        """Set token."""

        self.token = token
        self.expires_in = expires_in

        if token:
            try:
                self.token_info = jwt_token_analyzer(token)
            except AuthenticationError:
                pass

    def get_credentials_pair(self) -> tuple[str, str]:
        """Get credentials (RFC AWS & Basic)."""

        if not self.credentials:
            raise AuthenticationError('Missing credentials.')
        if not self.credentials.get('username'):
            raise AuthenticationError('Please provide a username')
        if not self.credentials.get('password'):
            raise AuthenticationError('Please provide a password')

        return self.credentials['username'], self.credentials['password']

    def to_dict(self) -> dict[str, Any]:
        """Get user as dict."""

        return {
            'auth_schema': self.auth_schema,
            'auth_tech': self.auth_tech,
            'auth_type': self.auth_type,
            'credentials': self.credentials,
            'token': self.token,
            'refresh_token': self.refresh_token,
            'expires_in': self.expires_in,
            'expired_token': self.expired_token,
            'token_info': self.token_info,
        }


class UserManager:

    """User manager."""

    _users: dict[str, User]

    def __init__(
        self,
        users: dict[str, User] | None = None,
    ) -> None:
        """Initialize the User manager."""

        if not users:
            users = {}

        self._users: dict[str, User] = users

    def reset(self) -> None:
        """Reset the user manager."""

        self._users = {}

    @property
    def users(self) -> dict[str, User]:
        """Get all users."""

        return self._users
