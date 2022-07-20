"""Manage Client auth flow."""

import json
import time
from copy import deepcopy
from importlib import resources
from typing import Any

import jsonschema  # type: ignore[import]
from jsonschema import ValidationError

from multiauth import static
from multiauth.config import PY_MULTIAUTH_LOGGER as logger
from multiauth.handlers import auth_handler, reauth_handler
from multiauth.manager import User, UserManager
from multiauth.providers.aws import aws_signature
from multiauth.types.errors import InvalidConfigurationError
from multiauth.types.http import HTTPMethod
from multiauth.types.interfaces import IMultiAuth
from multiauth.types.main import AuthTech, Token


class MultiAuth(IMultiAuth):

    """Multiauth manager."""

    def __init__(
        self,
        auths: dict,
        users: dict,
    ) -> None:
        """Initialize the Auth manager."""

        self.validate(auths, users)

        self._manager: UserManager = UserManager(self.serialize_users(auths, users))
        self._headers: dict[str, dict] = {}
        self._auths = auths

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

        return self._auths

    @staticmethod
    def validate(auths: dict, users: dict) -> None:
        """Validate the auth schema and users with json schema."""

        # Load the json schema from static
        with resources.open_text(static, 'auth_schema.json') as f:
            json_schema = json.load(f)

        auth_tech_link: dict[str, str] = {}
        s_users = ', '.join(auth_tech_link.keys())

        for auth_name, auth in auths.items():
            if auth is None or not isinstance(auth, dict):
                raise InvalidConfigurationError(message='auth is None or is not a dict', path=f'$.auth.{auth_name}')
            if 'tech' not in auth:
                raise InvalidConfigurationError(message='\'tech\' is a required property', path=f'$.auth.{auth_name}')
            if auth['tech'] not in json_schema:
                raise ValueError(f'\'{auth["tech"]}\' is not a valid auth tech')
            auth_tech_link[auth_name] = auth['tech']
            try:
                jsonschema.validate(auth, json_schema[auth['tech']]['authSchema'])
            except ValidationError as e:
                raise InvalidConfigurationError(message=e.message, path=f'$.auth.{auth_name}' + str(e.json_path)[2:]) from e

        for username, user in users.items():
            if user is None or not isinstance(user, dict):
                raise InvalidConfigurationError(message='user is None or is not a dict', path=f'$.users.{username}')
            if 'auth' not in user:
                raise InvalidConfigurationError(message='\'auth\' is a required property inside a user', path=f'$.users.{username}')
            if user['auth'] not in auth_tech_link:
                raise InvalidConfigurationError(
                    message=f'The authentication references user \'{user["auth"]}\' but the only users defined are: {s_users}', path=f'$.users.{username}.auth'
                )
            try:
                jsonschema.validate(user, json_schema[auth_tech_link[user['auth']]]['userSchema'])
            except ValidationError as e:
                raise InvalidConfigurationError(message=e.message, path=f'$.users.{username}' + e.json_path[2:]) from e

    @staticmethod
    def serialize_users(auths: dict, users: dict) -> dict[str, User]:
        """Serialize raw user to valid config format."""

        users = deepcopy(users)

        for user, user_info in users.items():

            schema = auths[user_info['auth']]

            _user_credientials: dict[str, Any] = deepcopy(user_info)
            del _user_credientials['auth']

            _user: User = User({
                'auth_schema': user_info['auth'],
                'auth_tech': AuthTech.NOAUTH if user_info['auth'] is None else AuthTech(schema['tech']),
                'credentials': _user_credientials,
            })

            users[user] = _user

        return users

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
                self._auths[user_info.auth_schema],
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
        logger.info(f'Authenticating user: {username}')
        auth_response = auth_handler(self._auths, user_info)
        if auth_response and isinstance(auth_response, dict):
            self._headers[username] = auth_response['headers']
            logger.info(f'Authentication successful for {username}')

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
                    self._auths,
                    user_info,
                    refresh_token,
                )

            else:
                auth_response = auth_handler(
                    self._auths,
                    user_info,
                )

            if auth_response and isinstance(auth_response, dict):
                self._headers[username] = auth_response['headers']
                logger.info('Reauthentication Successful')

        headers = headers or {}
        if not no_auth:
            headers |= self._headers.get(username, {})

        return headers, None if no_auth else username
