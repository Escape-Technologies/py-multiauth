from http import HTTPMethod
from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.http_core.entities import HTTPHeader, HTTPLocation
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, UserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction
from multiauth.lib.store.user import User
from multiauth.lib.store.variables import AuthenticationVariable


class OAuthClientCredentialsUserPreset(UserPreset):
    username: UserName = Field(description='The username of the user.')
    password: str = Field(description='The password of the user.')


class OAuthClientCredentialsPreset(BasePreset):
    type: Literal['oauth_client_credentials'] = 'oauth_client_credentials'

    server_url: str = Field(description='The URL of the token endpoint of the OpenIDConnect server')

    client_id: str = Field(description='The client ID to use for the OAuth requests')
    client_secret: str = Field(description='The client secret to use for the OAuth requests')

    users: Sequence[OAuthClientCredentialsUserPreset] = Field(
        description='A list of users to create',
    )

    def to_procedure_configuration(self) -> ProcedureConfiguration:
        return ProcedureConfiguration(
            name=ProcedureName(self.name),
            injections=[
                TokenInjection(
                    location=HTTPLocation.HEADER,
                    key='Authorization',
                    prefix='Bearer ',
                    variable=VariableName('access_token'),
                ),
            ],
            operations=[
                HTTPRunnerConfiguration(
                    parameters=HTTPRequestParameters(
                        url=self.server_url,
                        method=HTTPMethod.POST,
                        headers=[
                            HTTPHeader(name='Content-Type', values=['application/x-www-form-urlencoded']),
                            HTTPHeader(name='Accept', values=['application/json']),
                        ],
                        body=(
                            'grant_type=client_credentials'
                            f'&client_id={self.client_id}'
                            f'&client_secret={self.client_secret}'
                        ),
                    ),
                    extractions=[
                        TokenExtraction(
                            location=HTTPLocation.BODY,
                            name=VariableName('access_token'),
                            key='access_token',
                        ),
                    ],
                ),
            ],
        )

    def to_users(self) -> list[User]:
        return [
            User(
                name=UserName(user.name),
                variables=[
                    AuthenticationVariable(name=VariableName('username'), value=user.username),
                    AuthenticationVariable(name=VariableName('password'), value=user.password),
                ],
                credentials=user.to_credentials(),
                procedure=ProcedureName(self.name),
                refresh=None,
            )
            for user in self.users
        ]
