"""User manager."""

import time
from typing import Any, Dict, Optional, Tuple, cast

from multiauth.entities.errors import AuthenticationError, ExpiredTokenError
from multiauth.entities.interfaces import IUser
from multiauth.entities.main import AuthTech, AuthType, JWTToken, Token
from multiauth.helpers import jwt_token_analyzer


# pylint: disable=too-many-instance-attributes
class User(IUser):

    """User entity."""

    def __init__(
        self,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Init user."""

        self.reset()

        if kwargs:
            for key, value in kwargs.items():
                if not key.startswith('_'):
                    key = '_' + key

                setattr(self, key, value)

        for token in [self.token, self.refresh_token]:
            if not token:
                continue

            serialized_token = jwt_token_analyzer(token)
            if serialized_token.get('exp'):
                self.expires_in = float(cast(str, serialized_token['exp'])) - time.time()
                if self.expires_in < 0:
                    raise ExpiredTokenError('Token expired.')

    def reset(self) -> None:
        """Reset user."""

        self._auth_schema: Optional[str] = None
        self._auth_tech: AuthTech = AuthTech.PUBLIC
        self._auth_type: Optional[AuthType] = None
        self._credentials: Optional[Dict[str, Any]] = None
        self._expired_token: Optional[Token] = None
        self._expires_in: Optional[float] = None
        self._headers: Optional[Dict[str, Any]] = None
        self._refresh_token: Optional[Token] = None
        self._token_info: Optional[JWTToken] = None
        self._token: Optional[Token] = None

    @property
    def auth_schema(self) -> Optional[str]:
        """Get auth schema."""

        return self._auth_schema

    @auth_schema.setter
    def auth_schema(
        self,
        value: Optional[str],
    ) -> None:
        """Set auth schema."""

        self._auth_schema = value

    @property
    def auth_tech(self) -> AuthTech:
        """Get auth tech."""

        return self._auth_tech

    @auth_tech.setter
    def auth_tech(
        self,
        value: AuthTech,
    ) -> None:
        """Set auth tech."""

        self._auth_tech = value

    @property
    def auth_type(self) -> Optional[AuthType]:
        """Get the authentication type."""

        return self._auth_type

    @auth_type.setter
    def auth_type(
        self,
        auth_type: Optional[AuthType],
    ) -> None:
        """Set the authentication type."""

        self._auth_type = auth_type

    @property
    def credentials(self) -> Optional[Dict[str, Any]]:
        """Get credentials."""

        return self._credentials

    @credentials.setter
    def credentials(
        self,
        value: Dict[str, Any],
    ) -> None:
        """Set credentials."""

        self._credentials = value

    @property
    def expired_token(self) -> Optional[Token]:
        """Get the expired token."""

        return self._expired_token

    @expired_token.setter
    def expired_token(
        self,
        token: Optional[Token],
    ) -> None:
        """Set the expired token."""

        self._expired_token = token

    @property
    def expires_in(self) -> Optional[float]:
        """Get the expiration time."""

        return self._expires_in

    @expires_in.setter
    def expires_in(
        self,
        expires_in: Optional[float],
    ) -> None:
        """Set the expiration time."""

        self._expires_in = expires_in

    @property
    def headers(self) -> Optional[Dict[str, Any]]:
        """Get headers."""

        return self._headers

    @property
    def refresh_token(self) -> Optional[Token]:
        """Get the refresh token."""

        return self._refresh_token

    @refresh_token.setter
    def refresh_token(
        self,
        token: Optional[Token],
    ) -> None:
        """Set the refresh token."""

        self._refresh_token = token

    @property
    def token_info(self) -> Optional[JWTToken]:
        """Get the token info."""

        return self._token_info

    @token_info.setter
    def token_info(
        self,
        token: Optional[JWTToken],
    ) -> None:
        """Set the token info."""

        self._token_info = token

    @property
    def token(self) -> Optional[Token]:
        """Get the token."""

        return self._token

    @token.setter
    def token(
        self,
        token: Optional[Token],
    ) -> None:
        """Set the token."""

        self._token = token

    def set_token(
        self,
        token: Optional[Token],
        expires_in: Optional[float],
    ) -> None:
        """Set token."""

        self.token = token
        self.expires_in = expires_in

        if token:
            try:
                self.token_info = jwt_token_analyzer(token)
            except AuthenticationError:
                pass

    def get_credentials_pair(self) -> Tuple[str, str]:
        """Get credentials (RFC AWS & Basic)."""

        if not self.credentials:
            raise AuthenticationError('Missing credentials.')
        if not self.credentials.get('username'):
            raise AuthenticationError('Please provide a username')
        if not self.credentials.get('password'):
            raise AuthenticationError('Please provide a password')

        return self.credentials['username'], self.credentials['password']

    def to_dict(self) -> Dict[str, Any]:
        """Get user as Dict."""

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

    _users: Dict[str, User]

    def __init__(
        self,
        users: Optional[Dict[str, User]] = None,
    ) -> None:
        """Initialize the User manager."""

        if not users:
            users = {}

        self._users: Dict[str, User] = users

    def reset(self) -> None:
        """Reset the user manager."""

        self._users = {}

    @property
    def users(self) -> Dict[str, User]:
        """Get all users."""

        return self._users
