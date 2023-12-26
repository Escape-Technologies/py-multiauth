import datetime
import json
from typing import Any

from multiauth.revamp.configuration import (
    MultiauthConfiguration,
)
from multiauth.revamp.lib.http_core.entities import HTTPRequest, HTTPResponse
from multiauth.revamp.lib.procedure import Procedure
from multiauth.revamp.lib.store.authentication import Authentication, AuthenticationStore, AuthenticationStoreException
from multiauth.revamp.lib.store.user import User
from multiauth.revamp.lib.store.variables import AuthenticationVariable

DEFAULT_TTL_SECONDS = 10 * 24 * 60 * 60  # Default session ttl is 10 days


class MultiAuthException(Exception):
    pass


class MissingUserException(MultiAuthException):
    user_name: str

    def __init__(self, user_name: str) -> None:
        self.user_name = user_name

    def __str__(self) -> str:
        return f'Invalid user name. User `{self.user_name}` not registered in users list.'


class MissingProcedureException(MultiAuthException):
    procedure_name: str

    def __init__(self, procedure_name: str) -> None:
        self.procedure_name = procedure_name

    def __str__(self) -> str:
        return f'Invalid procedure name. Procedure `{self.procedure_name}` not registered in procedures list.'


class Multiauth:
    """
    Multiauth is the main entrypoint of the library. It is responsible for running the authentication procedures.
    Every authentication procedures should be run through a Multiauth instance.
    """

    configuration: MultiauthConfiguration

    procedures: dict[str, Procedure]
    users: dict[str, User]

    authentication_store: AuthenticationStore

    def __init__(self, configuration: MultiauthConfiguration, seed: list[HTTPResponse] | None = None) -> None:
        seed = seed or []

        self.configuration = configuration

        self.procedures = {}
        self.users = {}

        self.authentication_store = AuthenticationStore()

        for procedure_configuration in configuration.procedures:
            self.procedures[procedure_configuration.name] = Procedure(procedure_configuration)
        for user in configuration.users:
            self.users[user.name] = user

        for procedure in self.procedures.values():
            procedure.load_responses(seed)

    def _get_user(self, user_name: str) -> User:
        user = self.users.get(user_name)
        if not user:
            raise MissingUserException(user_name)
        return user

    def _get_authentication_object(self, user_name: str) -> Authentication:
        try:
            user = self.authentication_store.get(user_name)
        except AuthenticationStoreException as e:
            raise e
        except Exception as e:
            raise MultiAuthException(
                f'Unexpected error when retrieving authentication object of user `{user_name}`.',
            ) from e
        return user

    def _get_procedure(
        self,
        user_name: str,
    ) -> Procedure:
        user = self._get_user(user_name)

        procedure_name = user.authentication.procedure
        procedure = self.procedures.get(procedure_name)

        if not procedure:
            raise MissingProcedureException(procedure_name)

        return procedure

    def get_http_response(self, user_name: str, step: int) -> tuple[HTTPRequest, HTTPResponse] | None:
        """
        Runs the HTTP request declared at the given step of the procedure of the provided user.

        - Raises a `MissingUserException` if the provided user_name is not declared in the multiauth configuration
        - Raises a `MissingProcedureException` if the provided user relies on a procedure that
        is not declared in the multiauth configuration.
        """
        user = self._get_user(user_name)
        procedure = self._get_procedure(user_name)
        return procedure.request(user, step)

    def extract_variables(self, user_name: str, response: HTTPResponse, step: int) -> list[AuthenticationVariable]:
        """
        Runs the extractions declared at the given step of the procedure of the provided user,
        from the provided HTTP response.

        - Raises a `MissingProcedureException` if the provided user relies on a procedure that
        is not declared in the multiauth configuration.
        """
        procedure = self._get_procedure(user_name)
        return procedure.extract(response, step)

    def authenticate(
        self,
        user_name: str,
    ) -> tuple[Authentication, list[tuple[HTTPRequest, HTTPResponse, list[AuthenticationVariable]]]]:
        """
        Runs the authentication procedure of the provided user.

        - Raises a `MissingUserException` if the provided user_name is not declared in the multiauth configuration
        - Raises a `MissingProcedureException` if the provided user relies on a procedure that
        is not declared in the multiauth configuration.
        """
        user = self._get_user(user_name)
        procedure = self._get_procedure(user_name)

        authentication, records = procedure.authenticate(user)

        # @todo(maxence@escape): implement automated expiration detection from the authentication content
        detected_ttl_seconds: int | None = None
        # In case of a user-provided ttl for this user, use it instead of any ttl declared before
        ttl_seconds = detected_ttl_seconds or user.session_ttl_seconds or DEFAULT_TTL_SECONDS

        expiration = datetime.datetime.now() + datetime.timedelta(seconds=ttl_seconds)
        self.authentication_store.store(user_name, authentication, expiration)

        return authentication, records

    def should_refresh(self, user_name: str) -> bool:
        """
        Assess the expiration status of an user.

        - Raises an UnauthenticatedUserException if no authentication object has been provided yet for this user
        """
        return self.authentication_store.is_expired(user_name)

    def refresh(
        self,
        user_name: str,
    ) -> tuple[Authentication, list[tuple[HTTPRequest, HTTPResponse, list[AuthenticationVariable]]], int]:
        """
        Refresh the authentication object of a given user.

        - If no refresh procedure is provided in the user configuration, the procedure provided in the user
        authentication configuration will be used instead.
        - If the user has not been authenticated yet, the authentication procedure will be run instead.
        - Raises a `MissingUserException` if the provided user_name is not declared in the multiauth configuration
        - Raises a `MissingProcedureException` if the provided user relies on a procedure that
        is not declared in the multiauth configuration.
        - Raises a `MissingProcedureException` if the provided user relies on a refresh procedure that
        is not declared in the multiauth configuration.
        """
        user = self._get_user(user_name)
        try:
            base_authentication = self.authentication_store.get(user_name)
        except AuthenticationStoreException:
            # @todo(maxence@escape.tech): Record this event when it occurs
            # If the user is not authenticated already, authenticate it instead
            return self.authenticate(user_name)

        # Default to the authentication procedure
        refresh_procedure = self._get_procedure(user_name)

        # If the user has a refresh procedure, use it instead of the authentication procedure
        if user.refresh is not None and user.refresh.procedure is not None:
            refresh_procedure = self._get_procedure(user.refresh.procedure)

        # Run the procedure
        refreshed_authentication, records = refresh_procedure.authenticate(user)

        # If the user has a refresh procedure, and the `keep` flag is enabled, merge the current authentication object
        if user.refresh is not None and user.refresh.keep:
            refreshed_authentication = Authentication.merge(base_authentication, refreshed_authentication)

        # @todo(maxence@escape): implement automated expiration detection from the authentication content
        detected_ttl_seconds: int | None = None
        # In case of a user-provided ttl for this user, use it instead of any ttl declared before
        ttl_seconds = detected_ttl_seconds or user.session_ttl_seconds or DEFAULT_TTL_SECONDS

        expiration = datetime.datetime.now() + datetime.timedelta(seconds=ttl_seconds)

        # Store the new authentication object
        self.authentication_store.store(user_name, refreshed_authentication, expiration)
        refresh_count = self.authentication_store.store(user_name, refreshed_authentication)

        return refreshed_authentication, records, refresh_count

    @staticmethod
    def from_json_string(raw_configuration_string: str) -> 'Multiauth':
        """
        Static function responsible for parsing a raw stringified JSON configuration
        input into a validated Multiauth object.
        """
        configuration = MultiauthConfiguration.model_validate_json(raw_configuration_string)
        return Multiauth(configuration)

    @staticmethod
    def from_file(path: str) -> 'Multiauth':
        """
        Static function responsible for parsing a raw stringified JSON configuration
        input, read from a file into a validated Multiauth object.
        """
        try:
            with open(path) as f:
                raw_configuration = f.read()
        except Exception as e:
            raise MultiAuthException(f'Could not read configuration file at path `{path}`.') from e
        return Multiauth.from_json_string(raw_configuration)

    @staticmethod
    def from_any(raw_configuration: Any) -> 'Multiauth':
        """
        Static function responsible for parsing a JSON-serializable object representing a multiauth configuration,
        into a validated Multiauth object.
        """
        try:
            return Multiauth.from_json_string(json.dumps(raw_configuration))
        except Exception as e:
            raise MultiAuthException('Could not serialized configuration object') from e
