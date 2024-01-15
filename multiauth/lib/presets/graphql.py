import json
from http import HTTPMethod
from typing import Literal, NewType, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName
from multiauth.lib.http_core.entities import HTTPEncoding, HTTPHeader, HTTPLocation
from multiauth.lib.injection import BaseInjection
from multiauth.lib.presets.base import (
    BaseExtraction,
    BasePreset,
    HTTPRequestParameters,
    UserPreset,
)
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRunnerConfiguration
from multiauth.lib.store.user import User

GraphQLQuery = NewType('GraphQLQuery', str)


def safe_json_loads(s: str) -> dict:
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return {}


class GraphQLUserPreset(UserPreset):
    variables: dict[str, str] = Field(description='The variables of the GraphQL query containing the user credentials.')


class GraphQLPreset(BasePreset):
    type: Literal['graphql'] = 'graphql'

    name: ProcedureName = Field(default='My GraphQL Preset', description='The arbitrary name given to the preset.')

    url: str = Field(description='The URL of the GraphQL authentication endpoint.')
    query: GraphQLQuery = Field(
        description='The templated GraphQL inside the `query` field of the JSON body of the HTTP request.',
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

    extract: BaseExtraction = Field(
        default=BaseExtraction(location=HTTPLocation.BODY, key='token'),
        description='The extraction of the GraphQL query containing the user credentials.',
    )

    inject: BaseInjection = Field(
        default=BaseInjection(location=HTTPLocation.HEADER, key='Authorization', prefix='Bearer '),
        description='The injection of the GraphQL query containing the user credentials.',
    )

    users: Sequence[GraphQLUserPreset] = Field(
        description='A list of users with credentials contained in the GraphQL `variables` of the query',
    )

    def to_procedure_configuration(self) -> ProcedureConfiguration:
        return ProcedureConfiguration(
            name=ProcedureName(self.name),
            operations=[
                HTTPRunnerConfiguration(
                    parameters=HTTPRequestParameters(
                        url=self.url,
                        method=HTTPMethod.POST,
                        headers=[
                            HTTPHeader(name='Accept', values=[HTTPEncoding.JSON]),
                        ],
                    ),
                ),
            ],
        )

    def to_users(self) -> list[User]:
        res: list[User] = []

        for user in self.users:
            creds = user.to_credentials()
            creds.body = {
                'query': self.query,
                'variables': user.variables,
            }
            res.append(
                User(
                    name=UserName(user.name),
                    credentials=creds,
                    procedure=ProcedureName(self.name),
                ),
            )

        return res
