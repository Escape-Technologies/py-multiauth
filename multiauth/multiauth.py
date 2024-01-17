import json
from typing import Any

from multiauth.configuration import (
    MultiauthConfiguration,
)
from multiauth.exceptions import MissingProcedureException, MissingUserException, MultiAuthException
from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.audit.events.events import (
    HTTPFailureEvent,
    HTTPRequestEvent,
    HTTPResponseEvent,
    ProcedureAbortedEvent,
    ProcedureSkippedEvent,
    ValidationAttemptedEvent,
    ValidationFailedEvent,
    ValidationSucceededEvent,
)
from multiauth.lib.entities import ProcedureName, UserName
from multiauth.lib.http_core.entities import HTTPRequest
from multiauth.lib.http_core.request import send_request
from multiauth.lib.procedure import ISOExpirationTimestamp, Procedure, default_expiration_date
from multiauth.lib.store.authentication import (
    Authentication,
    AuthenticationStore,
    AuthenticationStoreException,
    UnauthenticatedUserException,
)
from multiauth.lib.store.user import Credentials, User


class Multiauth:
    """
    Multiauth is the main entrypoint of the library. It is responsible for running the authentication procedures.
    Every authentication procedures should be run through a Multiauth instance.
    """

    configuration: MultiauthConfiguration

    procedures: dict[ProcedureName, Procedure]
    users: dict[UserName, User]

    authentication_store: AuthenticationStore

    def __init__(self, configuration: MultiauthConfiguration) -> None:
        self.configuration = configuration

        self.procedures = {}
        self.users = {}

        self.authentication_store = AuthenticationStore()

        if configuration.proxy is not None:
            for procedure in configuration.procedures or []:
                for operation in procedure.operations:
                    operation.parameters.proxy = configuration.proxy

        expanded = configuration.expand()
        for procedure_configuration in expanded.procedures or []:
            self.procedures[procedure_configuration.name] = Procedure(procedure_configuration)
        for user in expanded.users or []:
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

        procedure_name = user.procedure

        if user.refresh is not None and user.refresh.procedure is not None:
            procedure_name = user.refresh.procedure

        if procedure_name is None:
            return None

        procedure = self.procedures.get(procedure_name)

        if not procedure:
            raise MissingProcedureException(procedure_name)

        return procedure

    def authenticate_users(
        self,
    ) -> dict[UserName, tuple[Authentication, EventsList, ISOExpirationTimestamp, Exception | None]]:
        """
        Runs the authentication for all users in the configuration. Retrocompatibility purposes with MultiAuth v2.
        """
        return {user_name: self.authenticate(user_name) for user_name in self.users.keys()}

    @property
    def headers_by_user(self) -> dict[UserName, dict[str, str]]:
        """
        Returns a dictionary of headers by user name. Used for retrocompatibility purposes with MultiAuth v2.
        """
        return {user: self.authentication_store.get(user)[0].all_headers for user in self.users}

    def authenticate(
        self,
        user_name: UserName,
    ) -> tuple[Authentication, EventsList, ISOExpirationTimestamp, Exception | None]:
        """
        Runs the authentication procedure of the provided user.

        - Raises a `MissingUserException` if the provided user_name is not declared in the multiauth configuration
        - Raises a `MissingProcedureException` if the provided user relies on a procedure that
        is not declared in the multiauth configuration.
        """
        user = self._get_user(user_name)
        authentication = Authentication.from_credentials(user.credentials or Credentials())
        expiration = default_expiration_date()

        error: Exception | None = None
        events = EventsList()

        if user.procedure is not None:
            try:
                procedure = self._get_authentication_procedure(user_name)
                procedure_authentication, procedure_events, expiration, error = procedure.run(user)
                events.extend(procedure_events)
                authentication = Authentication.merge(authentication, procedure_authentication)
            except Exception as e:
                events.append(ProcedureAbortedEvent(reason='unknown', description=f'Unknown error: {e}'))
                error = e
                expiration = default_expiration_date()
        else:
            events.append(ProcedureSkippedEvent(user_name=user_name))

        self.authentication_store.store(user_name, authentication, expiration)

        return (
            authentication,
            events,
            ISOExpirationTimestamp(expiration.isoformat()),
            error,
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
    ) -> tuple[Authentication, EventsList, ISOExpirationTimestamp, Exception | None]:
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
        error: Exception | None = None

        user = self._get_user(user_name)
        try:
            base_authentication, _ = self.authentication_store.get(user_name)
        except AuthenticationStoreException:
            # @todo(maxence@escape.tech): Record this event when it occurs
            # If the user is not authenticated already, authenticate it instead
            return self.authenticate(user_name)

        refresh_procedure = self._get_refresh_procedure(user_name)

        if refresh_procedure is None:
            # If the user has no procedure at all (no base and no refresh procedures), return the base authentication
            return (
                base_authentication,
                EventsList(ProcedureSkippedEvent(user_name=user_name)),
                ISOExpirationTimestamp(default_expiration_date().isoformat()),
                None,
            )

        refreshed_authentication = Authentication.empty()
        # Run the procedure
        try:
            refreshed_authentication, events, expiration, error = refresh_procedure.run(user.refresh_user)
        except Exception as e:
            events.append(ProcedureAbortedEvent(reason='unknown', description=f'Unexpected: {e}'))
            error = e
            expiration = default_expiration_date()

        # If the user has a refresh procedure, and the `keep` flag is enabled, merge the current authentication object
        if user.refresh is not None and user.refresh.keep:
            refreshed_authentication = Authentication.merge(base_authentication, refreshed_authentication)

        # Store the new authentication object
        self.authentication_store.store(user_name, refreshed_authentication, expiration)

        return refreshed_authentication, events, ISOExpirationTimestamp(expiration.isoformat()), error

    def test(self, user_name: UserName, request: HTTPRequest) -> tuple[bool, EventsList, Exception | None]:
        """
        Test the authentication object of a given user.
        Will send a request to the provided URL using the credentials of the given user.
        """
        events = EventsList()
        events.append(ValidationAttemptedEvent(user_name=user_name))

        try:
            authentication, expiration = self.authentication_store.get(user_name)
        except UnauthenticatedUserException as e:
            events.append(ValidationFailedEvent(reason='unauthenticated', description=str(e), user_name=user_name))
            return False, events, e
        except Exception as e:
            events.append(ValidationFailedEvent(reason='unknown', description=str(e), user_name=user_name))
            return False, events, e

        for header in authentication.headers:
            request.headers.append(header)
        for cookie in authentication.cookies:
            request.cookies.append(cookie)
        for query_parameters in authentication.query_parameters:
            request.query_parameters.append(query_parameters)

        if self.configuration.proxy:
            request.proxy = self.configuration.proxy

        events.append(HTTPRequestEvent(request=request))
        response = send_request(request)

        if isinstance(response, HTTPFailureEvent):
            events.append(ValidationFailedEvent(reason='http_error', description=str(response), user_name=user_name))
            return False, events, Exception('Received HTTP error during validation')

        if response.status_code in [401, 403]:
            events.append(HTTPResponseEvent(response=response, severity='error'))
            events.append(
                ValidationFailedEvent(
                    reason='http_error',
                    description=f'Received status code {response.status_code}',
                    user_name=user_name,
                ),
            )
            return False, events, Exception(f'Received HTTP status code {response.status_code} during validation')

        events.append(
            HTTPResponseEvent(response=response, severity='info' if response.status_code < 400 else 'warning'),
        )

        events.append(ValidationSucceededEvent(user_name=user_name))
        return True, events, None

    def sign(*args: Any, **kwargs: Any) -> dict[str, str]:
        """
        Used for AWS Signature.
        @todo(antoine@escape.tech): Implement this
        """
        if args:
            return {}
        if kwargs:
            return {}
        return {}

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
            if raw_configuration is None:
                return Multiauth(MultiauthConfiguration.public())
            return Multiauth.from_json_string(json.dumps(raw_configuration))
        except Exception as e:
            raise MultiAuthException('Could not serialized configuration object') from e
