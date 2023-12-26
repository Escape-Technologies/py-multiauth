import abc
from typing import Annotated, Union

from pydantic import BaseModel, Field

from multiauth.revamp.lib.http_core.entities import HTTPRequest, HTTPResponse
from multiauth.revamp.lib.runners.base import BaseRequestRunner
from multiauth.revamp.lib.runners.basic import BasicRequestConfiguration
from multiauth.revamp.lib.runners.graphql import GraphQLRequestConfiguration
from multiauth.revamp.lib.runners.http import HTTPRequestConfiguration
from multiauth.revamp.lib.store.authentication import Authentication
from multiauth.revamp.lib.store.user import User
from multiauth.revamp.lib.store.variables import AuthenticationVariable

RequestConfigurationType = Annotated[
    Union[HTTPRequestConfiguration, GraphQLRequestConfiguration, BasicRequestConfiguration],
    Field(discriminator='tech'),
]


class ProcedureConfiguration(BaseModel, abc.ABC):
    name: str = Field(description='The name of the procedure.')
    requests: list[RequestConfigurationType] = Field(default_factory=list)


class Procedure:
    """
    Agnostic procedure executor that can run a list of requests and extract variables from the responses
    """

    configuration: ProcedureConfiguration
    runners: list[BaseRequestRunner]

    # The dictionnary where the extracted variables are stored
    variables: dict[str, AuthenticationVariable]

    def __init__(self, configuration: ProcedureConfiguration):
        self.configuration = configuration

        self.runners = []
        self.variables = {}

        for request in self.configuration.requests:
            self.runners.append(request.get_runner())

    def extract(self, response: HTTPResponse, runner_id: int) -> list[AuthenticationVariable]:
        """
        Runs the extractions of the provided runner_id to extract variables from an HTTP response,
        store them and return them. If `runner_id` is greater than the number of runners, an empty list is returned.
        """
        variables: list[AuthenticationVariable] = []
        if runner_id >= len(self.runners):
            return variables
        runner = self.runners[runner_id]
        for variable in runner.extract(response):
            variables.append(variable)

        return variables

    def load_responses(self, responses: list[HTTPResponse]) -> None:
        """
        Run the extractions corresponding to a sequence of HTTP response for the given procedure,
        and store the resulting variables. The nth response will go through the extraction declared
        with the nth runner of the procedure. If the number of responses exceeds the number of steps in
        the procedure, the extra responses will be ignored.
        """
        for i, response in enumerate(responses):
            for variable in self.extract(response, i):
                self.variables[variable.name] = variable

    def request(self, user: User, step: int) -> tuple[HTTPRequest, HTTPResponse] | None:
        """
        Execute the nth request of the procedure for the given user, and return the corresponding request/response pair.
        """
        if step >= len(self.runners):
            return None

        runner = self.runners[step]
        return runner.request(user)

    def inject(self, user: User) -> Authentication:
        """
        Inject the variables extracted from the procedure into the user's authentication. Injections are performed
        using the stored variables, so the procedure requests must have been run before calling this method.
        """
        authentication = Authentication.empty()

        for injection in user.authentication.injections:
            authentication = Authentication.merge(
                authentication,
                Authentication.inject(injection, list(self.variables.values())),
            )

        return authentication

    def authenticate(
        self,
        user: User,
    ) -> tuple[Authentication, list[tuple[HTTPRequest, HTTPResponse, list[AuthenticationVariable]]]]:
        """
        Execute the full procedure for the given user, including extractions, and return the resulting authentication
        and the list of request/response/variables tuples that were generated during the procedure.
        If one of the procedure requests fails, it will generate an authentication object from the extracted variables
        up to that resuest.
        """
        records: list[tuple[HTTPRequest, HTTPResponse, list[AuthenticationVariable]]] = []

        for runner in self.runners:
            res = runner.request(user)
            if res is None:
                break

            request, response = res
            variables = runner.extract(response)
            records.append((request, response, variables))

            for variable in variables:
                self.variables[variable.name] = variable

        return self.inject(user), records
