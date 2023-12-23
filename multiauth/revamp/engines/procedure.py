import abc
from typing import Annotated, Union

from pydantic import BaseModel, Field

from multiauth.revamp.engines.base import BaseRequestRunner
from multiauth.revamp.engines.basic import BasicRequestConfiguration
from multiauth.revamp.engines.graphql import GraphQLRequestConfiguration
from multiauth.revamp.engines.http import HTTPRequestConfiguration
from multiauth.revamp.lib.http_core.entities import HTTPRequest, HTTPResponse
from multiauth.revamp.store.authentication import Authentication, merge_authentications
from multiauth.revamp.store.user import User
from multiauth.revamp.store.variables import AuthenticationVariable

RequestConfigurationType = Annotated[
    Union[HTTPRequestConfiguration, GraphQLRequestConfiguration, BasicRequestConfiguration],
    Field(discriminator='tech'),
]


class ProcedureConfiguration(BaseModel, abc.ABC):
    name: str
    requests: list[RequestConfigurationType] = Field(default_factory=list)


class Procedure:
    configuration: ProcedureConfiguration
    runners: list[BaseRequestRunner]
    variables: dict[str, AuthenticationVariable]

    def __init__(self, configuration: ProcedureConfiguration):
        self.configuration = configuration

        self.runners = []
        self.variables = {}

        for request in self.configuration.requests:
            self.runners.append(request.get_runner())

    def extract(self, response: HTTPResponse, runner_id: int) -> list[AuthenticationVariable]:
        variables: list[AuthenticationVariable] = []
        if runner_id >= len(self.runners):
            return variables
        runner = self.runners[runner_id]
        for variable in runner.extract(response):
            variables.append(variable)

        return variables

    def load_responses(self, responses: list[HTTPResponse]) -> None:
        for i, response in enumerate(responses):
            for variable in self.extract(response, i):
                self.variables[variable.name] = variable

    def request(self, user: User, step: int) -> tuple[HTTPRequest, HTTPResponse] | None:
        if step >= len(self.runners):
            return None

        runner = self.runners[step]
        return runner.request(user)

    def inject(self, user: User) -> Authentication:
        authentication = Authentication.empty()

        for injection in user.injections:
            authentication = merge_authentications(
                authentication,
                Authentication.inject(injection, list(self.variables.values())),
            )

        return authentication

    def authenticate(
        self,
        user: User,
    ) -> tuple[Authentication, list[tuple[HTTPRequest, HTTPResponse, list[AuthenticationVariable]]]]:
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
