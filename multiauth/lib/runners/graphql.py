import json
from http import HTTPMethod
from typing import Any, Literal

from pydantic import BaseModel, Field

from multiauth.lib.http_core.entities import (
    HTTPHeader,
)
from multiauth.lib.http_core.mergers import merge_bodies, merge_headers
from multiauth.lib.runners.base import BaseRunnerConfiguration
from multiauth.lib.runners.http import (
    HTTPExtractionType,
    HTTPRequestParameters,
    HTTPRequestRunner,
    HTTPRunnerConfiguration,
)
from multiauth.lib.store.variables import AuthenticationVariable, interpolate_string


class GraphQLVariable(BaseModel):
    name: str
    value: Any


class GraphQLRequestParameters(HTTPRequestParameters):
    query: str = Field(
        description=(
            'The GraphQL query to send. Will be added to the `query` field of the JSON body of the HTTP request.'
        ),
        examples=[
            '\n'.join(
                [
                    'mutation($username: String!, $password: String!) {',
                    '   login(username: $username, password: $password) {',
                    '       access_token',
                    '       refresh_token',
                    '   }',
                    '}',
                ],
            ),
            'query { __typename }',
        ],
    )
    variables: list[GraphQLVariable] | None = Field(
        default=None,
        description=(
            'The variables to send with the query. Will be added to the `variables` field of'
            'the JSON body of the HTTP request.'
        ),
    )
    method: HTTPMethod = Field(
        default=HTTPMethod.POST,
        description='The HTTP method to use to send the request. By default, POST is used.',
    )


class GraphQLRunnerConfiguration(BaseRunnerConfiguration):
    tech: Literal['graphql'] = 'graphql'
    extractions: list[HTTPExtractionType] = Field(
        default_factory=list,
        description=(
            'The list of extractions to run at the end of the operation.'
            'For HTTP operations, variables are extracted from the response.'
        ),
    )
    parameters: GraphQLRequestParameters = Field(
        description=(
            'The parameters of the GraphQL request to send. At least a query and a GraphQL '
            'endpoint are required. By default, POST is used as the HTTP method, and the request is sent as JSON.'
        ),
    )

    def to_http(self) -> HTTPRunnerConfiguration:
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
            'variables': {variable.name: variable.value for variable in self.parameters.variables or []},
        }

        body = merge_bodies(body, graphql_body)

        return HTTPRunnerConfiguration(
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
                body=body,
                proxy=self.parameters.proxy,
            ),
        )

    def get_runner(self) -> 'GraphQLRequestRunner':
        return GraphQLRequestRunner(self)


class GraphQLRequestRunner(HTTPRequestRunner):
    graphql_request_configuration: GraphQLRunnerConfiguration

    def __init__(self, graphql_request_configuration: GraphQLRunnerConfiguration) -> None:
        self.graphql_request_configuration = graphql_request_configuration
        http_procedure = graphql_request_configuration.to_http()
        super().__init__(http_procedure)

    def interpolate(self, variables: list[AuthenticationVariable]) -> 'GraphQLRequestRunner':
        graphql_request_configuration_str = self.graphql_request_configuration.model_dump_json()
        graphql_request_configuration_str = interpolate_string(graphql_request_configuration_str, variables)
        graphql_request_configuration = GraphQLRunnerConfiguration.model_validate_json(
            graphql_request_configuration_str,
        )

        return GraphQLRequestRunner(graphql_request_configuration)
