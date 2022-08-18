"""Manage Client auth flow."""

import json
import logging
import os
import time
from contextvars import ContextVar
from copy import deepcopy
from importlib import resources
from typing import Any, Dict, Optional, Tuple

import jsonschema  # type: ignore[import]
from jsonschema import ValidationError

from multiauth import static
from multiauth.entities.errors import InvalidConfigurationError
from multiauth.entities.http import HTTPMethod
from multiauth.entities.interfaces import IMultiAuth
from multiauth.entities.main import AuthTech, Token
from multiauth.handlers import auth_handler, reauth_handler
from multiauth.manager import User, UserManager
from multiauth.providers.aws import aws_signature
from multiauth.utils import setup_logger

ctx_store: ContextVar['MultiAuth'] = ContextVar('multiauth_instance')


def load_authrc(
    logger: logging.Logger,
    authrc: Optional[str] = None,
) -> Tuple[Dict, Dict]:
    """Load authrc file."""

    filepath = authrc or os.getenv('AUTHRC')
    if not filepath:
        if os.path.exists('.authrc'):
            filepath = '.authrc'
        elif os.path.exists(os.path.expanduser('~/.multiauth/.authrc')):
            filepath = os.path.expanduser('~/.multiauth/.authrc')

    if not filepath:
        raise InvalidConfigurationError('authrc file not found', path='$')

    logger.info(f'loading authrc file: {filepath}')

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not 'auth' in data:
        raise InvalidConfigurationError('auth section not found', path='$.auth')

    if not 'users' in data:
        raise InvalidConfigurationError('users section not found', path='$.users')

    return data['auth'], data['users']


class MultiAuth(IMultiAuth):

    """Multiauth manager."""

    def __new__(
        cls,
        auths: Optional[Dict] = None,
        users: Optional[Dict] = None,
        authrc: Optional[str] = None,
        logger: Optional[logging.Logger] = None,  # pylint: disable=unused-argument
    ) -> 'MultiAuth':
        """Create a new instance of the Auth manager."""

        try:
            instance = ctx_store.get()
        except LookupError:
            instance = None

        if instance is not None:
            if instance.auths == auths and instance._manager.users == users and instance._authrc == authrc:
                return instance

        instance = super().__new__(cls)
        ctx_store.set(instance)
        return instance

    def __init__(
        self,
        auths: Optional[Dict] = None,
        users: Optional[Dict] = None,
        authrc: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize the Auth manager."""

        self._logger = logger or setup_logger()
        self._authrc = authrc

        if auths is None or users is None:
            auths, users = load_authrc(self._logger, authrc)

        self.validate(auths, users)

        self._manager: UserManager = UserManager(self.serialize_users(auths, users))
        self._headers: Dict[str, Dict] = {}
        self._auths = auths

    @property
    def headers(self) -> Dict[str, Dict]:
        """Fetch all user's headers."""

        return self._headers

    @property
    def auths(self) -> Dict[str, User]:
        """Fetch all auths methods."""

        return self._auths

    @property
    def users(self) -> Dict[str, User]:
        """Fetch all users of the internal manager."""

        return self._manager.users

    @property
    def schemas(self) -> Dict:
        """Fetch internal schemas."""

        return self._auths

    @staticmethod
    def validate(
        auths: Dict,
        users: Dict,
    ) -> None:
        """Validate the auth schema and users with json schema."""

        # Load the json schema from static
        with resources.open_text(static, 'auth_schema.json') as f:
            json_schema = json.load(f)

        auth_tech_link: Dict[str, str] = {}
        s_users = ', '.join(auth_tech_link.keys())

        for auth_name, auth in auths.items():
            if auth is None or not isinstance(auth, Dict):
                raise InvalidConfigurationError(message='auth is None or is not a Dict', path=f'$.auth.{auth_name}')
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
            if user is None or not isinstance(user, Dict):
                raise InvalidConfigurationError(message='user is None or is not a Dict', path=f'$.users.{username}')
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
    def serialize_users(
        auths: Dict,
        users: Dict,
    ) -> Dict[str, User]:
        """Serialize raw user to valid config format."""

        users = deepcopy(users)

        for user, user_info in users.items():

            schema = auths[user_info['auth']]

            _user_credientials: Dict[str, Any] = deepcopy(user_info)
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
        headers: Dict[str, str],
        formatted_payload: Any,
    ) -> Dict[str, str]:
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
    ) -> Tuple[Dict[str, str], str]:
        """Authenticate the client using the current user."""

        # Reset the user's headers
        self._headers[username] = {}

        user_info: User = self._manager.users[username]

        # Call the auth handler
        self._logger.info(f'Authenticating user: {username}')
        auth_response = auth_handler(self._auths, user_info)
        if auth_response and isinstance(auth_response, Dict):
            self._headers[username] = auth_response['headers']
            self._logger.info(f'Authentication successful for {username}')

        # In case we provided custom headers, we need to merge them with the ones we got from auth_handler
        if user_info.headers:
            self._headers[username].update(user_info.headers)

        return self._headers[username], username

    def authenticate_users(self) -> Dict[str, Optional[Token]]:
        """Authenticate all the users."""

        tokens: Dict[str, Optional[Token]] = {}
        for user, user_info in self._manager.users.items():
            self._logger.info(f'Authenticating users : {user}')

            if user_info.auth_schema:
                self.authenticate(user)

            tokens[user] = self._manager.users[user].token

        return tokens

    def reauthenticate(
        self,
        username: str,
        additional_headers: Optional[Dict[str, str]] = None,
        no_auth: bool = False,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        """Reauthentication of the user in case of token expiry."""

        headers = additional_headers or {}
        user_info = self._manager.users[username]
        expiry_time = user_info.expires_in
        refresh_token = user_info.refresh_token

        # If there is no expiry date, no reauthentication is necessary
        # If the expiry date is more then the current time, no reauthentication is necessary
        if expiry_time and expiry_time < time.time():
            self._logger.info('Token is expired')

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

            if auth_response and isinstance(auth_response, Dict):
                self._headers[username] = auth_response['headers']
                self._logger.info('Reauthentication Successful')

        if not no_auth:
            headers.update(self._headers.get(username, {}))

        return headers, None if no_auth else username
