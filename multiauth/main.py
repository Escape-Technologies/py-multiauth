"""Manage Client auth flow."""

import time
from typing import Any

from multiauth.config import PY_MULTIAUTH_LOGGER as logger
from multiauth.handlers import auth_handler, reauth_handler
from multiauth.manager import User, UserManager
from multiauth.providers.aws import aws_signature
from multiauth.types.abst import MultiAuthBase
from multiauth.types.http import HTTPMethod
from multiauth.types.main import AuthTech, Token


class MultiAuth(MultiAuthBase):

    """Multiauth manager."""

    def __init__(
        self,
        schemas: dict,
        users: dict[str, User],
    ) -> None:
        """Initialize the Auth manager."""

        self._manager: UserManager = UserManager(users)
        self._headers: dict[str, dict] = {}
        self._schemas = schemas

        # Link users to schemas
        for user in self._manager.users.values():
            if user.auth_tech == AuthTech.NOAUTH:
                if not user.auth_schema in self._schemas:
                    continue

                user.auth_tech = self._schemas[user.auth_schema]['tech']

    @property
    def headers(self) -> dict[str, dict]:
        """Fetch all headers of the internal manager."""

        return self._headers

    @property
    def users(self) -> dict[str, User]:
        """Fetch all users of the internal manager."""

        return self._manager.users

    @property
    def schemas(self) -> dict:
        """Fetch internal schemas."""

        return self._schemas

    def sign(
        self,
        url: str,
        username: str,
        method: HTTPMethod,
        headers: dict[str, str],
        formatted_payload: Any,
    ) -> dict[str, str]:
        """Sign a payload before sending it.

        This is a mandatory for AWS Signature.
        """

        if self._manager.users[username].auth_type == 'aws_signature':
            user_info: User = self._manager.users[username]
            auth_headers = aws_signature(
                user_info,
                self._schemas[user_info.auth_schema],
                headers,
                method,
                formatted_payload,
                url,
            )
            headers.update(auth_headers['headers'])

        return headers

    def authenticate(
        self,
        username: str,
    ) -> tuple[dict[str, str], str]:
        """Authenticate the client using the current user."""

        # Reset the user's headers
        self._headers[username] = {}

        user_info: User = self._manager.users[username]

        # Call the auth handler
        print(f'Authenticating users : {username}')
        auth_response = auth_handler(self._schemas, user_info)
        if auth_response and isinstance(auth_response, dict):
            self._headers[username] = auth_response['headers']
            logger.info('Authentication Successful')

        # In case we provided custom headers, we need to merge them with the ones we got from auth_handler
        if user_info.headers:
            self._headers[username] |= user_info.headers

        return self._headers[username], username

    def authenticate_users(self) -> dict[str, Token | None]:
        """Authenticate all the users."""

        tokens: dict[str, Token | None] = {}
        for user, user_info in self._manager.users.items():
            logger.info(f'Authenticating users : {user}')

            if user_info.auth_schema:
                self.authenticate(user)

            tokens[user] = self._manager.users[user].token

        return tokens

    def reauthenticate(
        self,
        username: str,
        headers: dict[str, str] | None = None,
        no_auth: bool = False,
    ) -> tuple[dict[str, str], str | None]:
        """Reauthentication of the user in case of token expiry."""

        user_info = self._manager.users[username]
        expiry_time = user_info.expires_in
        refresh_token = user_info.refresh_token

        # If there is no expiry date, no reauthentication is necessary
        # If the expiry date is more then the current time, no reauthentication is necessary
        if expiry_time and expiry_time < time.time():
            logger.info('Token is expired')

            user_info.expired_token = user_info.token

            # If this condition is true, we have to reauthenticate the user
            # But before, we have to check if refresh token exists
            if refresh_token:
                auth_response = reauth_handler(
                    self._schemas,
                    user_info,
                    refresh_token,
                )

            else:
                auth_response = auth_handler(
                    self._schemas,
                    user_info,
                )

            if auth_response and isinstance(auth_response, dict):
                self._headers[username] = auth_response['headers']
                logger.info('Reauthentication Successful')

        headers = headers or {}
        if not no_auth:
            headers |= self._headers.get(username, {})

        return headers, None if no_auth else username
