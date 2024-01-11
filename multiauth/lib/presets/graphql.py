from http import HTTPMethod
from typing import Literal

from pydantic import BaseModel, Field

from multiauth.lib.http_core.entities import HTTPHeader, HTTPLocation
from multiauth.lib.presets.base import BasePreset, UserPresetBase
from multiauth.lib.procedure import ProcedureConfiguration, ProcedureName
from multiauth.lib.runners.http import HTTPBodyExtraction, HTTPRequestParameters, HTTPRunnerConfiguration
from multiauth.lib.store.injection import TokenInjection
from multiauth.lib.store.user import Credentials, User, UserName
from multiauth.lib.store.variables import VariableName


class HTTPParamsPresent(BaseModel):
    url: str = Field(description='The URL the HTTP authentication server')
    method: HTTPMethod = Field(
        default=HTTPMethod.POST,
        description='The HTTP Method to use to execute authentication the query',
    )
    headers: list[HTTPHeader] = Field(
        default_factory=list,
        description='The headers to use to execute authentication the query',
    )
    body: dict[str, str] = Field(
        default_factory=dict,
        description='The body to use to execute authentication the query',
    )


class GraphQLParamsPreset(HTTPParamsPresent):
    query: str = Field(description='The templated GraphQL Query to execute to authenticate the user')


class GraphQLUserPreset(UserPresetBase):
    variables: dict[str, str] = Field(
        default_factory=dict,
        description='The GraphQL Variables representing the user crendentials injected in the GraphQL Query',
    )


class GraphQLInjectPreset(BaseModel):
    location: HTTPLocation = Field(
        default=HTTPLocation.HEADER,
        description='The location where to inject the token',
    )
    key: str = Field(
        default='Authorization',
        description='The key where to inject the token',
    )
    prefix: str = Field(
        default='Bearer ',
        description='The prefix to add to the token before injecting it',
    )


class GraphQLPreset(BasePreset):
    type: Literal['graphql'] = 'graphql'

    request: GraphQLParamsPreset
    extract: HTTPBodyExtraction
    inject: GraphQLInjectPreset

    users: list[GraphQLUserPreset] = Field(default_factory=list, description='A list of users to create')

    def to_procedure_configuration(self) -> ProcedureConfiguration:
        return ProcedureConfiguration(
            name=ProcedureName(self.name),
            operations=[
                HTTPRunnerConfiguration(
                    parameters=HTTPRequestParameters(
                        url=self.request.url,
                        method=HTTPMethod.POST,
                        headers=[
                            HTTPHeader(name='Accept', values=['application/json']),
                        ],
                        body={'query': self.request.query},
                    ),
                    extractions=[
                        HTTPBodyExtraction(
                            name=VariableName('token'),
                            location=self.extract.location,
                            key=self.extract.key,
                        ),
                    ],
                ),
            ],
        )

    def to_users(self) -> list[User]:
        return [
            User(
                name=UserName(user.name),
                credentials=Credentials(body={'variables': user.variables}),
                procedure=ProcedureName(self.name),
                injections=[
                    TokenInjection(
                        location=self.inject.location,
                        key=self.inject.key,
                        prefix=self.inject.prefix,
                        variable=VariableName('token'),
                    ),
                ],
                refresh=None,
            )
            for user in self.users
        ]
