import base64
from typing import Literal

from multiauth.revamp.lib.audit.events.base import EventsList
from multiauth.revamp.lib.http_core.entities import (
    HTTPHeader,
)
from multiauth.revamp.lib.http_core.mergers import merge_headers
from multiauth.revamp.lib.runners.base import BaseRunnerConfiguration, RunnerException
from multiauth.revamp.lib.runners.http import (
    HTTPRequestParameters,
    HTTPRequestRunner,
    HTTPRunnerConfiguration,
)
from multiauth.revamp.lib.store.user import User
from multiauth.revamp.lib.store.variables import AuthenticationVariable, VariableName, interpolate_string


class BasicRunnerConfiguration(BaseRunnerConfiguration):
    name: str
    tech: Literal['basic'] = 'basic'
    parameters: HTTPRequestParameters

    def to_http(self) -> HTTPRunnerConfiguration:
        return HTTPRunnerConfiguration(
            extractions=[],
            parameters=self.parameters,
        )

    def get_runner(self) -> 'BasicRequestRunner':
        return BasicRequestRunner(self)


def build_basic_headers(username: str, password: str) -> HTTPHeader:
    value = 'Basic ' + base64.b64encode(f'{username}:{password}'.encode()).decode()
    return HTTPHeader(name='Authorization', values=[value])


class BasicRequestRunner(HTTPRequestRunner):
    basic_request_configuration: BasicRunnerConfiguration

    def __init__(self, configuration: BasicRunnerConfiguration) -> None:
        self.basic_request_configuration = configuration
        super().__init__(self.basic_request_configuration.to_http())

    def run(self, user: User) -> tuple[list[AuthenticationVariable], EventsList, RunnerException | None]:
        if not user.credentials.username or not user.credentials.password:
            raise ValueError(f'User {user.name} is missing a username or password.')

        header = build_basic_headers(user.credentials.username, user.credentials.password)

        basic_user = User.from_user(user)
        basic_user.credentials.headers = merge_headers(
            user.credentials.headers,
            [header],
        )

        variables, events, exception = super().run(basic_user)
        variables.append(AuthenticationVariable(name=VariableName('basic-header-value'), value=header.values[0]))

        return variables, events, exception

    def interpolate(self, variables: list[AuthenticationVariable]) -> 'BasicRequestRunner':
        basic_request_configuration = self.basic_request_configuration.model_dump_json()
        basic_request_configuration = interpolate_string(basic_request_configuration, variables)
        graphql_request_configuration = BasicRunnerConfiguration.model_validate_json(basic_request_configuration)

        return BasicRequestRunner(graphql_request_configuration)
