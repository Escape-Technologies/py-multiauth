import datetime
import json
from typing import Any

from multiauth.configuration import (
    MultiauthConfiguration,
)
from multiauth.exceptions import MissingProcedureException, MissingUserException, MultiAuthException
from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.audit.events.events import ProcedureSkippedEvent
from multiauth.lib.procedure import Procedure
from multiauth.lib.store.authentication import Authentication, AuthenticationStore, AuthenticationStoreException
from multiauth.lib.store.user import User, UserName

DEFAULT_TTL_SECONDS = 10 * 24 * 60 * 60  # Default session ttl is 10 days


class Multiauth:
    """
    Multiauth is the main entrypoint of the library. It is responsible for running the authentication procedures.
    Every authentication procedures should be run through a Multiauth instance.
    """

    configuration: MultiauthConfiguration

    procedures: dict[str, Procedure]
    users: dict[str, User]

    authentication_store: AuthenticationStore

    def __init__(self, configuration: MultiauthConfiguration) -> None:
        self.configuration = configuration

        self.procedures = {}
        self.users = {}

        self.authentication_store = AuthenticationStore()

        for preset in configuration.presets:
            preset_procedure_configuration = preset.to_procedure_configuration()
            self.procedures[preset.name] = Procedure(preset_procedure_configuration)
            users = preset.to_users()
            for user in users:
                self.users[f'{preset.name}_{user.name}'] = user

        for procedure_configuration in configuration.procedures:
            self.procedures[procedure_configuration.name] = Procedure(procedure_configuration)
        for user in configuration.users:
            self.users[user.name] = user

    def _get_user(self, user_name: UserName) -> User:
        user = self.users.get(user_name)
        if not user:
            raise MissingUserException(user_name)
        return user

    def _get_authentication_procedure(
        self,
        user_name: UserName,
    ) -> Procedure:
        user = self._get_user(user_name)

        procedure_name = user.procedure
        if procedure_name is None:
            raise MissingProcedureException('No procedure name provided for user `{user_name}`')

        procedure = self.procedures.get(procedure_name)

        if not procedure:
            raise MissingProcedureException(procedure_name)

        return procedure

    def _get_refresh_procedure(
        self,
        user_name: UserName,
    ) -> Procedure | None:
        user = self._get_user(user_name)

        if user.refresh is None:
            return None

        if user.refresh.procedure is None:
            return None

        procedure_name = user.refresh.procedure
        procedure = self.procedures.get(procedure_name)

        if not procedure:
            raise MissingProcedureException(procedure_name)

        return procedure

    def authenticate(
        self,
        user_name: UserName,
    ) -> tuple[Authentication, EventsList, int]:
        """
        Runs the authentication procedure of the provided user.

        - Raises a `MissingUserException` if the provided user_name is not declared in the multiauth configuration
        - Raises a `MissingProcedureException` if the provided user relies on a procedure that
        is not declared in the multiauth configuration.
        """
        user = self._get_user(user_name)
        authentication = Authentication.from_credentials(user.credentials)

        if user.procedure is not None:
            procedure = self._get_authentication_procedure(user_name)
            procedure_authentication, events = procedure.run(user)
            authentication = Authentication.merge(authentication, procedure_authentication)
        else:
            events = EventsList(ProcedureSkippedEvent(user_name=user_name))

        # @todo(maxence@escape): implement automated expiration detection from the authentication content
        detected_ttl_seconds: int | None = None
        # In case of a user-provided ttl for this user, use it instead of any ttl declared before
        ttl_seconds = detected_ttl_seconds or user.session_ttl_seconds or DEFAULT_TTL_SECONDS

        expiration = datetime.datetime.now() + datetime.timedelta(seconds=ttl_seconds)
        self.authentication_store.store(user_name, authentication, expiration)

        return (
            authentication,
            events,
            0,
        )

    def should_refresh(self, user_name: UserName) -> bool:
        """
        Assess the expiration status of an user.

        - Raises an UnauthenticatedUserException if no authentication object has been provided yet for this user
        """
        return self.authentication_store.is_expired(user_name)

    def refresh(
        self,
        user_name: UserName,
    ) -> tuple[Authentication, EventsList, int]:
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
            base_authentication, _ = self.authentication_store.get(user_name)
        except AuthenticationStoreException:
            # @todo(maxence@escape.tech): Record this event when it occurs
            # If the user is not authenticated already, authenticate it instead
            return self.authenticate(user_name)

        # Default to the authentication procedure
        refresh_procedure = self._get_authentication_procedure(user_name)

        # Else go for the specific refresh procedure
        if (rp := self._get_refresh_procedure(user_name)) is not None:
            refresh_procedure = rp

        # Run the procedure
        refreshed_authentication, events = refresh_procedure.run(user.refresh_user)

        # If the user has a refresh procedure, and the `keep` flag is enabled, merge the current authentication object
        if user.refresh is not None and user.refresh.keep:
            refreshed_authentication = Authentication.merge(base_authentication, refreshed_authentication)

        # @todo(maxence@escape): implement automated expiration detection from the authentication content
        detected_ttl_seconds: int | None = None
        # In case of a user-provided ttl for this user, use it instead of any ttl declared before
        ttl_seconds = detected_ttl_seconds or user.session_ttl_seconds or DEFAULT_TTL_SECONDS

        expiration = datetime.datetime.now() + datetime.timedelta(seconds=ttl_seconds)

        # Store the new authentication object
        refresh_count = self.authentication_store.store(user_name, refreshed_authentication, expiration)

        return refreshed_authentication, events, refresh_count

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
