import json
from http import HTTPMethod
from typing import Literal, NewType, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.extraction import TokenExtraction
from multiauth.lib.http_core.entities import HTTPEncoding, HTTPHeader, HTTPLocation
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration
from multiauth.lib.store.user import Credentials, User

GraphQLQuery = NewType('GraphQLQuery', str)


def safe_json_loads(s: str) -> dict:
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return {}


class GraphQLUserPreset(BaseUserPreset):
    username: UserName = Field(description='The name of the user.')
    variables: dict[str, str] = Field(description='The variables of the GraphQL query containing the user credentials.')


class GraphQLPreset(BasePreset):
    type: Literal['graphql'] = 'graphql'

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

    extract: TokenExtraction = Field(
        default=TokenExtraction(location=HTTPLocation.BODY, key='token', name=VariableName('token')),
        description='The extraction of the GraphQL query containing the user credentials.',
    )

    inject: TokenInjection = Field(
        default=TokenInjection(location=HTTPLocation.HEADER, key='Authorization', prefix='Bearer '),
        description='The injection of the GraphQL query containing the user credentials.',
    )

    users: Sequence[GraphQLUserPreset] = Field(
        description='A list of users with credentials contained in the GraphQL `variables` of the query',
    )

    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        return [
            ProcedureConfiguration(
                name=ProcedureName(self.slug),
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
            ),
        ]

    def to_users(self) -> list[User]:
        res: list[User] = []

        for user in self.users:
            creds = Credentials(
                body={
                    'query': self.query,
                    'variables': user.variables,
                },
            )
            res.append(
                User(
                    name=UserName(user.username),
                    credentials=creds,
                    procedure=self.slug,
                ),
            )

        return res
