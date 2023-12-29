import abc
from typing import Annotated, Union

from pydantic import BaseModel, Field

from multiauth.entities.user import ProcedureName
from multiauth.revamp.exceptions import MissingProcedureException
from multiauth.revamp.lib.audit.events.base import Event
from multiauth.revamp.lib.audit.events.events import (
    ProcedureAbortedEvent,
    ProcedureEndedEvent,
    ProcedureStartedEvent,
)
from multiauth.revamp.lib.http_core.entities import HTTPRequest, HTTPResponse
from multiauth.revamp.lib.runners.base import BaseRequestRunner
from multiauth.revamp.lib.runners.basic import BasicRequestConfiguration
from multiauth.revamp.lib.runners.graphql import GraphQLRequestConfiguration
from multiauth.revamp.lib.runners.http import HTTPRequestConfiguration
from multiauth.revamp.lib.store.authentication import Authentication
from multiauth.revamp.lib.store.user import User
from multiauth.revamp.lib.store.variables import AuthenticationVariable, VariableName

RequestConfigurationType = Annotated[
    Union[HTTPRequestConfiguration, GraphQLRequestConfiguration, BasicRequestConfiguration],
    Field(discriminator='tech'),
]


class ProcedureConfiguration(BaseModel, abc.ABC):
    name: ProcedureName = Field(description='The name of the procedure.')
    requests: list[RequestConfigurationType] = Field(default_factory=list)


class Procedure:
    """
    Agnostic procedure executor that can run a list of requests and extract variables from the responses
    """

    configuration: ProcedureConfiguration
    runners: list[BaseRequestRunner]
    events: list[Event]

    # The dictionnary where the extracted variables are stored
    variables: dict[VariableName, AuthenticationVariable]

    def __init__(self, configuration: ProcedureConfiguration):
        self.configuration = configuration

        self.runners = []
        self.variables = {}
        self.events = []

        for request in self.configuration.requests:
            self.runners.append(request.get_runner())

    def extract(self, response: HTTPResponse, runner_id: int) -> tuple[list[AuthenticationVariable], list[Event]]:
        """
        Runs the extractions of the provided runner_id to extract variables from an HTTP response,
        store them and return them. If `runner_id` is greater than the number of runners, an empty list is returned.
        """
        events: list[Event] = []
        variables: list[AuthenticationVariable] = []

        if runner_id >= len(self.runners):
            return variables, events
        runner = self.runners[runner_id]
        variables, extraction_events = runner.extract(response)

        for event in extraction_events:
            events.append(event)
        for variable in variables:
            variables.append(variable)

        for event in events:
            self.events.append(event)

        return variables, events

    def load_responses(self, responses: list[HTTPResponse]) -> tuple[list[AuthenticationVariable], list[Event]]:
        """
        Run the extractions corresponding to a sequence of HTTP response for the given procedure,
        and store the resulting variables. The nth response will go through the extraction declared
        with the nth runner of the procedure. If the number of responses exceeds the number of steps in
        the procedure, the extra responses will be ignored.
        """
        events: list[Event] = []
        variables: list[AuthenticationVariable] = []

        for i, response in enumerate(responses):
            variables, extraction_events = self.extract(response, i)
            for event in extraction_events:
                events.append(event)
            for variable in variables:
                variables.append(variable)
                self.variables[variable.name] = variable

        for event in events:
            self.events.append(event)

        return variables, events

    def request(self, user: User, step: int) -> tuple[HTTPRequest, HTTPResponse | None, list[Event]]:
        """
        Execute the nth request of the procedure for the given user, and return the corresponding request/response pair.
        """
        if step >= len(self.runners):
            raise MissingProcedureException(f'Procedure {self.configuration.name} has no step {step}.')

        runner = self.runners[step]
        request, response, events = runner.request(user)

        for event in events:
            self.events.append(event)

        return request, response, events

    def inject(self, user: User) -> tuple[Authentication, list[Event]]:
        """
        Inject the variables extracted from the procedure into the user's authentication. Injections are performed
        using the stored variables, so the procedure requests must have been run before calling this method.
        """
        events: list[Event] = []
        authentication = Authentication.empty()

        for injection in user.authentication.injections:
            new_authentication, injection_events = Authentication.inject(injection, list(self.variables.values()))
            for event in injection_events:
                events.append(event)
            authentication = Authentication.merge(authentication, new_authentication)

        for event in events:
            self.events.append(event)

        return authentication, events

    def authenticate(
        self,
        user: User,
    ) -> tuple[Authentication, list[Event]]:
        """
        Execute the full procedure for the given user, including extractions, and return the resulting authentication
        and the list of request/response/variables tuples that were generated during the procedure.
        If one of the procedure requests fails, it will generate an authentication object from the extracted variables
        up to that request.
        """

        events: list[Event] = [ProcedureStartedEvent(user_name=user.name, procedure_name=self.configuration.name)]

        for i, runner in enumerate(self.runners):
            request, response, http_events = runner.interpolate(list(self.variables.values())).request(user)

            for event in http_events:
                events.append(event)

            if response is None:
                event = ProcedureAbortedEvent(reason='unknown', description='No response received.')
                events.append(event)
                return Authentication.empty(), events

            if response.status_code >= 400:
                events.append(
                    ProcedureAbortedEvent(
                        reason='http_error',
                        description=f'HTTP error {response.status_code} received at step {i} of procedure.',
                    ),
                )
                return Authentication.empty(), events

            variables, extraction_events = runner.extract(response)
            for event in extraction_events:
                events.append(event)
            for variable in variables:
                self.variables[variable.name] = variable

        authentication, injection_events = self.inject(user)
        for event in injection_events:
            events.append(event)

        events.append(ProcedureEndedEvent(user_name=user.name))
        for event in events:
            self.events.append(event)

        return authentication, events
