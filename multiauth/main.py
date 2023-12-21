"""Manage Client auth flow."""

import json
import logging
import os
import time
from copy import deepcopy
from importlib import resources
from typing import Any

import jsonschema

from multiauth import static
from multiauth.entities.errors import InvalidConfigurationError
from multiauth.entities.http import HTTPMethod
from multiauth.entities.main import AuthTech, Token
from multiauth.handlers import auth_handler, reauth_handler
from multiauth.helpers.logger import setup_logger
from multiauth.manager import User, UserManager
from multiauth.providers.aws import aws_signature


def load_authrc(
    logger: logging.Logger,
    authrc: str | None = None,
) -> tuple[dict, dict]:
    """Load authrc file."""

    filepath = authrc or os.getenv('AUTHRC')
    if not filepath:
        for path in ['.authrc', '.authrc.json']:
            if os.path.exists(path):
                filepath = path
                break
    elif os.path.exists(os.path.expanduser('~/.multiauth/.authrc')):
        filepath = os.path.expanduser('~/.multiauth/.authrc')

    if not filepath:
        raise InvalidConfigurationError('authrc file not found', path='$')

    logger.info(f'loading authrc file: {filepath}')

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'authentication' in data:
        data = data['authentication']

    if 'headers' in data:
        return load_headers(data['headers'])

    if 'methods' not in data:
        raise InvalidConfigurationError('methods section not found', path='$.methods')

    if 'users' not in data:
        raise InvalidConfigurationError('users section not found', path='$.users')

    return data['methods'], data['users']


def load_headers(headers: dict[str, str]) -> tuple[dict, dict]:
    """Creates a valid user and auth schema from the headers.

    This is used to be able to pass headers easily.
    """
    if not isinstance(headers, dict):
        raise InvalidConfigurationError('headers must be a dict', path='$.headers')
    auth = {'default_schema': {'tech': 'manual'}}
    users = {'default_user': {'auth': 'default_schema', 'headers': headers}}
    return auth, users


class MultiAuth:
    """Multiauth manager."""

    logger: logging.Logger
    authrc: str | None
    proxy: str | None

    manager: Any
    headers: dict[str, dict]
    methods: dict

    def __init__(
        self,
        methods: dict | None = None,
        users: dict | None = None,
        authrc: str | None = None,
        logger: logging.Logger | None = None,
        proxy: str | None = None,
    ) -> None:
        """Initialize the Auth manager."""

        self.logger = logger or setup_logger()
        self.authrc = authrc
        self.proxy = proxy

        if methods is None or users is None:
            methods, users = load_authrc(self.logger, authrc)

        self.validate(methods, users)

        self.manager = UserManager(self.serialize_users(methods, users))
        self.headers = {}
        self.methods = methods

    @property
    def users(self) -> dict[str, User]:
        """Fetch all users of the internal manager."""

        return self.manager.users

    @staticmethod
    def validate(
        methods: dict,
        users: dict,
    ) -> None:
        """Validate the auth schema and users with json schema."""

        # Load the json schema from static
        with resources.open_text(static, 'auth_schema.json') as f:
            json_schema = json.load(f)

        auth_tech_link: dict[str, str] = {}
        s_users = ', '.join(auth_tech_link.keys())

        for auth_name, auth in methods.items():
            if auth is None or not isinstance(auth, dict):
                raise InvalidConfigurationError(message='auth is None or is not a dict', path=f'$.auth.{auth_name}')
            if 'tech' not in auth:
                raise InvalidConfigurationError(message="'tech' is a required property", path=f'$.auth.{auth_name}')
            if auth['tech'] not in json_schema:
                raise InvalidConfigurationError(
                    message=f'\'{auth["tech"]}\' is not a valid auth tech',
                    path=f'$.auth.{auth_name}.tech',
                )
            auth_tech_link[auth_name] = auth['tech']
            try:
                jsonschema.validate(auth, json_schema[auth['tech']]['authSchema'])
            except (jsonschema.ValidationError, jsonschema.SchemaError) as e:
                raise InvalidConfigurationError(
                    message=e.message,
                    path=f'$.auth.{auth_name}' + str(e.json_path)[2:],
                ) from e

        for username, user in users.items():
            if user is None or not isinstance(user, dict):
                raise InvalidConfigurationError(message='user is None or is not a dict', path=f'$.users.{username}')
            if 'auth' not in user:
                raise InvalidConfigurationError(
                    message="'auth' is a required property inside a user",
                    path=f'$.users.{username}',
                )
            if user['auth'] not in auth_tech_link:
                raise InvalidConfigurationError(
                    message=f'Auth references user \'{user["auth"]}\' but the only users defined are: {s_users}',
                    path=f'$.users.{username}.auth',
                )
            try:
                jsonschema.validate(user, json_schema[auth_tech_link[user['auth']]]['userSchema'])
            except (jsonschema.ValidationError, jsonschema.SchemaError) as e:
                raise InvalidConfigurationError(message=e.message, path=f'$.users.{username}' + e.json_path[2:]) from e

    @staticmethod
    def serialize_users(
        methods: dict,
        users: dict,
    ) -> dict[str, User]:
        """Serialize raw user to valid config format."""

        users = deepcopy(users)

        for user, user_info in users.items():
            schema = methods[user_info['auth']]

            _user_credientials: dict[str, Any] = deepcopy(user_info)
            del _user_credientials['auth']

            _user: User = User(
                auth_schema=user_info['auth'],
                auth_tech=AuthTech.PUBLIC if user_info['auth'] is None else AuthTech(schema['tech']),
                credentials=_user_credientials,
            )

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

        if self.users[username].auth_type == 'aws_signature':
            user_info: User = self.users[username]
            auth_headers = aws_signature(
                user_info,
                self.methods[user_info.auth_schema],
                headers,
                method,
                formatted_payload,
                url,
            )
            headers.update(auth_headers.headers)

        return headers

    def authenticate(
        self,
        username: str,
    ) -> tuple[dict[str, str], str]:
        """Authenticate the client using the current user."""

        # Reset the user's headers
        self.headers[username] = {}

        user_info: User = self.users[username]

        # Call the auth handler
        self.logger.info(f'Authenticating user: {username}')
        auth_response = auth_handler(self.methods, user_info, proxy=self.proxy)
        if auth_response is not None:
            self.headers[username] = auth_response.headers
            self.logger.info(f'Authentication successful for {username}')

        # In case we provided custom headers, we need to merge them with the ones we got from auth_handler
        if user_info.headers:
            self.headers[username].update(user_info.headers)

        return self.headers[username], username

    def authenticate_users(self) -> dict[str, Token | None]:
        """Authenticate all the users."""

        tokens: dict[str, Token | None] = {}
        for user, user_info in self.users.items():
            self.logger.info(f'Authenticating users : {user}')

            if user_info.auth_schema:
                self.authenticate(user)

            tokens[user] = self.users[user].token

        return tokens

    def reauthenticate(
        self,
        username: str,
        additional_headers: dict[str, str] | None = None,
        public: bool = False,
    ) -> tuple[dict[str, str], str | None]:
        """Reauthentication of the user in case of token expiry.

        Args:
            username: The username of the user to reauthenticate.
            additional_headers: Additional headers to add to the returned headers.
            public: If True, do not authenticate the user.

        Returns:
            - The headers
            - The username of the user, if authenticated.
        """

        headers = additional_headers or {}
        user_info = self.users[username]
        expiry_time = user_info.expires_in
        refresh_token = user_info.refresh_token

        # If there is no expiry date, no reauthentication is necessary
        # If the expiry date is more then the current time, no reauthentication is necessary
        if expiry_time and expiry_time < time.time():
            self.logger.info('Token is expired')

            user_info.expired_token = user_info.token

            # If this condition is true, we have to reauthenticate the user
            # But before, we have to check if refresh token exists
            if refresh_token:
                auth_response = reauth_handler(
                    self.methods,
                    user_info,
                    refresh_token,
                    proxy=self.proxy,
                )

            else:
                auth_response = auth_handler(
                    self.methods,
                    user_info,
                    proxy=self.proxy,
                )

            if auth_response is not None:
                self.headers[username] = auth_response.headers
                self.logger.info('Reauthentication Successful')

        if not public:
            headers.update(self.headers.get(username, {}))

        return headers, None if public else username
