import abc
from typing import Annotated, Union

from pydantic import BaseModel, Field

from multiauth.lib import ProcedureName
from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.audit.events.events import (
    ProcedureAbortedEvent,
    ProcedureEndedEvent,
    ProcedureStartedEvent,
)
from multiauth.lib.runners.base import BaseRunner, RunnerException
from multiauth.lib.runners.basic import BasicRunnerConfiguration
from multiauth.lib.runners.digest import DigestRunnerConfiguration
from multiauth.lib.runners.graphql import GraphQLRunnerConfiguration
from multiauth.lib.runners.http import HTTPRunnerConfiguration
from multiauth.lib.runners.webdriver.runner import SeleniumRunnerConfiguration
from multiauth.lib.store.authentication import Authentication
from multiauth.lib.store.user import User
from multiauth.lib.store.variables import AuthenticationVariable, VariableName

OperationConfigurationType = Annotated[
    Union[
        HTTPRunnerConfiguration,
        GraphQLRunnerConfiguration,
        BasicRunnerConfiguration,
        SeleniumRunnerConfiguration,
        DigestRunnerConfiguration,
    ],
    Field(discriminator='tech'),
]


class ProcedureConfiguration(BaseModel, abc.ABC):
    name: ProcedureName = Field(description='The name of the procedure.')
    operations: list[OperationConfigurationType] = Field(default_factory=list)


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

    def inject(self, user: User) -> tuple[Authentication, EventsList]:
        """
        Inject the variables extracted from the procedure into the user's authentication. Injections are performed
        using the stored variables, so the procedure requests must have been run before calling this method.
        """
        events = EventsList()
        authentication = Authentication.empty()

        for injection in user.injections:
            new_authentication, injection_events = Authentication.inject(injection, list(self.variables.values()))
            for event in injection_events:
                events.append(event)
            authentication = Authentication.merge(authentication, new_authentication)

        for event in events:
            self.events.append(event)

        return authentication, events

    def run(
        self,
        user: User,
    ) -> tuple[Authentication, EventsList, RunnerException | None]:
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
                return Authentication.empty(), events, error

        authentication, injection_events = self.inject(user)
        for event in injection_events:
            events.append(event)

        events.append(ProcedureEndedEvent(user_name=user.name))
        for event in events:
            self.events.append(event)

        return authentication, events, None
