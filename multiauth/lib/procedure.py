import abc
from datetime import datetime, timedelta
from typing import Annotated, NewType, Union

from pydantic import Field

from multiauth.helpers.base_model import StrictBaseModel
from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.audit.events.events import (
    ProcedureAbortedEvent,
    ProcedureEndedEvent,
    ProcedureStartedEvent,
    TokenParsedEvent,
)
from multiauth.lib.entities import ProcedureName, VariableName
from multiauth.lib.injection import TokenInjection
from multiauth.lib.runners.base import BaseRunner, RunnerException
from multiauth.lib.runners.digest import DigestRunnerConfiguration
from multiauth.lib.runners.http import HTTPRunnerConfiguration
from multiauth.lib.runners.webdriver.runner import SeleniumRunnerConfiguration
from multiauth.lib.store.authentication import Authentication
from multiauth.lib.store.user import User
from multiauth.lib.store.variables import AuthenticationVariable
from multiauth.lib.token import parse_token

ISOExpirationTimestamp = NewType('ISOExpirationTimestamp', str)

DEFAULT_TTL_SECONDS = 10 * 24 * 60 * 60  # Default


def default_expiration_date() -> datetime:
    return datetime.now() + timedelta(seconds=DEFAULT_TTL_SECONDS)


OperationConfigurationType = Annotated[
    Union[
        HTTPRunnerConfiguration,
        SeleniumRunnerConfiguration,
        DigestRunnerConfiguration,
    ],
    Field(discriminator='tech'),
]

DEFAULT_TTL_SECONDS = 10 * 24 * 60 * 60  # Default session ttl is 10 days


class ProcedureConfiguration(StrictBaseModel, abc.ABC):
    name: ProcedureName = Field(
        description='The name of the procedure. It must be unique and is used to reference the procedure in users.',
    )
    operations: list[OperationConfigurationType] = Field(
        default_factory=list,
        description=(
            'The list of operations executed during the procedure. An operation is a '
            'unit transaction, like an HTTP request, or a Selenium script. '
            'Operations are ordered, and the variables extracted from an operation '
            'can be used in the next operations.'
        ),
    )
    injections: list[TokenInjection] = Field(
        default_factory=list,
        description=(
            'The list of injections to perform at the end of the procedure. '
            'Injections are used to inject the variables extracted from the procedure '
            'into the user authentication.'
        ),
    )


class Procedure:
    """
    Agnostic procedure executor that can run a list of requests and extract variables from the responses
    """

    configuration: ProcedureConfiguration
    runners: list[BaseRunner]
    events: EventsList

    # The dictionnary where the extracted variables are stored
    variables: dict[VariableName, AuthenticationVariable]

    def __init__(self, configuration: ProcedureConfiguration):
        self.configuration = configuration

        self.runners = []
        self.variables = {}
        self.events = EventsList()

        for request in self.configuration.operations:
            self.runners.append(request.get_runner())

    def inject(self, user: User) -> tuple[Authentication, EventsList, datetime]:
        """
        Inject the variables extracted from the procedure into the user's authentication. Injections are performed
        using the stored variables, so the procedure requests must have been run before calling this method.
        """
        events = EventsList()
        authentication = Authentication.empty()

        for injection in self.configuration.injections:
            injected_authentication, injection_events = injection.inject(list(self.variables.values()))
            events.extend(injection_events)
            authentication = Authentication.merge(authentication, injected_authentication)

        self.events.extend(events)

        # If the user has a session_ttl_seconds set, use it to compute the expiration date
        if user.session_ttl_seconds is not None:
            expiration = datetime.now() + timedelta(seconds=user.session_ttl_seconds)
        else:  # Otherwise, infer the expiration date of the first expiring token
            expirations: list[datetime] = []
            for variable in self.variables.values():
                token = parse_token(variable.value)
                if token is None:
                    continue

                self.events.append(TokenParsedEvent(token=token))
                if token.expiration is not None:
                    expirations.append(token.expiration)

            # Fall back to default expiration date if no token has an expiration date
            expiration = min(expirations) if len(expirations) > 0 else default_expiration_date()

        return (
            authentication,
            events,
            expiration,
        )

    def run(
        self,
        user: User,
    ) -> tuple[Authentication, EventsList, datetime, RunnerException | None]:
        """
        Execute the full procedure for the given user, including extractions, and return the resulting authentication
        and the list of request/response/variables tuples that were generated during the procedure.
        If one of the procedure requests fails, it will generate an authentication object from the extracted variables
        up to that request.
        """

        events = EventsList()
        events.append(ProcedureStartedEvent(user_name=user.name, procedure_name=self.configuration.name))

        for i, runner in enumerate(self.runners):
            variables = list(reversed(list(self.variables.values()) + user.variables))

            variables, run_events, error = runner.interpolate(variables).run(user)
            events.extend(run_events)

            for variable in variables:
                self.variables[variable.name] = variable

            if error is not None:
                events.append(
                    ProcedureAbortedEvent(
                        reason='runner_error',
                        description=f'Runner error at step {i} of procedure: {error}',
                    ),
                )
                return Authentication.empty(), events, default_expiration_date(), error

        authentication, injection_events, expiration = self.inject(user)
        for event in injection_events:
            events.append(event)

        events.append(ProcedureEndedEvent(user_name=user.name))
        for event in events:
            self.events.append(event)

        return authentication, events, expiration, None
