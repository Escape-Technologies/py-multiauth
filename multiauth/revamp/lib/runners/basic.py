import base64
from typing import Literal

from multiauth.revamp.lib.audit.events.base import Event
from multiauth.revamp.lib.http_core.entities import (
    HTTPHeader,
    HTTPRequest,
    HTTPResponse,
)
from multiauth.revamp.lib.http_core.mergers import merge_headers
from multiauth.revamp.lib.runners.base import BaseRequestConfiguration
from multiauth.revamp.lib.runners.http import (
    HTTPRequestConfiguration,
    HTTPRequestParameters,
    HTTPRequestRunner,
)
from multiauth.revamp.lib.store.user import User
from multiauth.revamp.lib.store.variables import AuthenticationVariable, interpolate_string


class BasicRequestConfiguration(BaseRequestConfiguration):
    name: str
    tech: Literal['basic'] = 'basic'
    parameters: HTTPRequestParameters

    def to_http(self) -> HTTPRequestConfiguration:
        return HTTPRequestConfiguration(
            extractions=[],
            parameters=self.parameters,
        )

    def get_runner(self) -> 'BasicRequestRunner':
        return BasicRequestRunner(self)


def build_basic_headers(username: str, password: str) -> HTTPHeader:
    value = 'Basic ' + base64.b64encode(f'{username}:{password}'.encode()).decode()
    return HTTPHeader(name='Authorization', values=[value])


class BasicRequestRunner(HTTPRequestRunner):
    basic_request_configuration: BasicRequestConfiguration

    def __init__(self, configuration: BasicRequestConfiguration) -> None:
        self.basic_request_configuration = configuration
        super().__init__(self.basic_request_configuration.to_http())

    def request(self, user: User) -> tuple[HTTPRequest, HTTPResponse | None, list[Event]]:
        if not user.credentials.username or not user.credentials.password:
            raise ValueError(f'User {user.name} is missing a username or password.')

        header = build_basic_headers(user.credentials.username, user.credentials.password)

        basic_user = User.from_user(user)
        basic_user.credentials.headers = merge_headers(
            user.credentials.headers,
            [header],
        )

        return super().request(basic_user)

    def extract(self, _response: HTTPResponse | None) -> tuple[list[AuthenticationVariable], list[Event]]:
        return [], []

    def interpolate(self, variables: list[AuthenticationVariable]) -> 'BasicRequestRunner':
        basic_request_configuration = self.basic_request_configuration.model_dump_json()
        basic_request_configuration = interpolate_string(basic_request_configuration, variables)
        graphql_request_configuration = BasicRequestConfiguration.model_validate_json(basic_request_configuration)

        return BasicRequestRunner(graphql_request_configuration)
