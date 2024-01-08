from http import HTTPMethod
from typing import Literal

from pydantic import Field

from multiauth.lib.http_core.entities import HTTPHeader, HTTPLocation
from multiauth.lib.presets.base import BasePreset
from multiauth.lib.procedure import ProcedureConfiguration, ProcedureName
from multiauth.lib.runners.http import HTTPBodyExtraction, HTTPRequestParameters, HTTPRunnerConfiguration
from multiauth.lib.store.injection import TokenInjection
from multiauth.lib.store.user import Credentials, User, UserAuthentication, UserName
from multiauth.lib.store.variables import AuthenticationVariable, VariableName


class OAuthClientCredentialsPreset(BasePreset):
    type: Literal['oauth_client_credentials'] = 'oauth_client_credentials'

    server_url: str = Field(description='The URL of the token endpoint of the OpenIDConnect server')

    client_id: str = Field(description='The client ID to use for the OAuth requests')
    client_secret: str = Field(description='The client secret to use for the OAuth requests')

    users: list[tuple[str, str]] = Field(default_factory=list, description='A list of users to create')

    def to_procedure_configuration(self) -> ProcedureConfiguration:
        return ProcedureConfiguration(
            name=ProcedureName(self.name),
            requests=[
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
                        HTTPBodyExtraction(
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
                name=UserName(username),
                variables=[
                    AuthenticationVariable(name=VariableName('username'), value=username),
                    AuthenticationVariable(name=VariableName('password'), value=password),
                ],
                credentials=Credentials(),
                authentication=UserAuthentication(
                    procedure=ProcedureName(self.name),
                    injections=[
                        TokenInjection(
                            location=HTTPLocation.HEADER,
                            key='Authorization',
                            prefix='Bearer ',
                            variable=VariableName('access_token'),
                        ),
                    ],
                ),
                refresh=None,
            )
            for username, password in self.users
        ]
