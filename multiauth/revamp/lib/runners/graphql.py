import json
from http import HTTPMethod
from typing import Any, Literal

from pydantic import BaseModel, Field

from multiauth.revamp.lib.http_core.entities import (
    HTTPHeader,
)
from multiauth.revamp.lib.http_core.mergers import merge_bodies, merge_headers
from multiauth.revamp.lib.runners.base import BaseRequestConfiguration
from multiauth.revamp.lib.runners.http import (
    HTTPExtraction,
    HTTPRequestConfiguration,
    HTTPRequestParameters,
    HTTPRequestRunner,
)
from multiauth.revamp.lib.store.variables import AuthenticationVariable, interpolate_string


class GraphQLVariable(BaseModel):
    name: str
    value: Any


class GraphQLRequestParameters(HTTPRequestParameters):
    query: str
    variables: list[GraphQLVariable] = Field(default_factory=list)
    method: HTTPMethod = Field(default=HTTPMethod.POST)


class GraphQLRequestConfiguration(BaseRequestConfiguration):
    tech: Literal['graphql'] = 'graphql'
    extractions: list[HTTPExtraction] = Field(default_factory=list)
    parameters: GraphQLRequestParameters

    def to_http(self) -> HTTPRequestConfiguration:
        body = {}
        if self.parameters.body is not None:
            try:
                json_body = json.loads(self.parameters.body)
                if isinstance(json_body, dict):
                    body = json_body
            except json.JSONDecodeError:
                pass

        graphql_body = {
            'query': self.parameters.query,
            'variables': {variable.name: variable.value for variable in self.parameters.variables},
        }

        body = merge_bodies(body, graphql_body)

        return HTTPRequestConfiguration(
            extractions=self.extractions,
            parameters=HTTPRequestParameters(
                url=self.parameters.url,
                method=self.parameters.method,
                headers=merge_headers(
                    self.parameters.headers,
                    [HTTPHeader(name='Content-Type', values=['application/json'])],
                ),
                cookies=self.parameters.cookies,
                query_parameters=self.parameters.query_parameters,
                body=self.parameters.body,
            ),
        )

    def get_runner(self) -> 'GraphQLRequestRunner':
        return GraphQLRequestRunner(self)


class GraphQLRequestRunner(HTTPRequestRunner):
    graphql_request_configuration: GraphQLRequestConfiguration

    def __init__(self, graphql_request_configuration: GraphQLRequestConfiguration) -> None:
        self.graphql_request_configuration = graphql_request_configuration
        http_procedure = graphql_request_configuration.to_http()
        super().__init__(http_procedure)

    def interpolate(self, variables: list[AuthenticationVariable]) -> 'GraphQLRequestRunner':
        graphql_request_configuration_str = self.graphql_request_configuration.model_dump_json()
        graphql_request_configuration_str = interpolate_string(graphql_request_configuration_str, variables)
        graphql_request_configuration = GraphQLRequestConfiguration.model_validate_json(
            graphql_request_configuration_str,
        )

        return GraphQLRequestRunner(graphql_request_configuration)
