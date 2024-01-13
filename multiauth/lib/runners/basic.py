import base64
from http import HTTPMethod
from typing import Literal

from pydantic import Field

from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.http_core.entities import (
    HTTPHeader,
)
from multiauth.lib.http_core.mergers import merge_headers
from multiauth.lib.runners.base import BaseRunnerConfiguration, RunnerException
from multiauth.lib.runners.http import (
    HTTPRequestParameters,
    HTTPRequestRunner,
    HTTPRunnerConfiguration,
    TokenExtraction,
)
from multiauth.lib.store.user import Credentials, User
from multiauth.lib.store.variables import AuthenticationVariable, VariableName, interpolate_string


class BasicRunnerConfiguration(BaseRunnerConfiguration):
    tech: Literal['basic'] = 'basic'
    parameters: HTTPRequestParameters = Field(
        description=('The parameters of the HTTP request used to test the username and password.'),
        examples=HTTPRequestParameters.examples(),
    )
    extractions: list[TokenExtraction] = Field(
        default_factory=list,
        description=('The extractions of the HTTP request used to test the username and password.'),
        examples=[
            *TokenExtraction.examples(),
        ],
    )

    @staticmethod
    def examples() -> list:
        return [
            BasicRunnerConfiguration(
                extractions=[],
                parameters=HTTPRequestParameters(
                    url='https://example.com',
                    method=HTTPMethod.GET,
                ),
            ),
        ]

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
        credentials = user.credentials or Credentials()
        request_credentials = Credentials.from_credentials(credentials)

        if not credentials.username or not credentials.password:
            raise ValueError(f'User {user.name} is missing a username or password.')

        header = build_basic_headers(credentials.username, credentials.password)
        request_credentials.headers = merge_headers(
            credentials.headers,
            [header],
        )

        basic_user = User.from_user(user)
        basic_user.credentials = request_credentials

        variables, events, exception = super().run(basic_user)
        variables.append(AuthenticationVariable(name=VariableName('basic-header-value'), value=header.values[0]))

        return variables, events, exception

    def interpolate(self, variables: list[AuthenticationVariable]) -> 'BasicRequestRunner':
        basic_request_configuration_str = self.basic_request_configuration.model_dump_json()
        basic_request_configuration_str = interpolate_string(basic_request_configuration_str, variables)
        basic_request_configuration = BasicRunnerConfiguration.model_validate_json(basic_request_configuration_str)

        return BasicRequestRunner(basic_request_configuration)
