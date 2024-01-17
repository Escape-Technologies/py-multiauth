from http import HTTPMethod
from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.http_core.entities import HTTPEncoding, HTTPHeader, HTTPLocation
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction
from multiauth.lib.store.user import User, UserRefresh
from multiauth.lib.store.variables import AuthenticationVariable


class OAuthClientCredentialsUserPreset(BaseUserPreset):
    username: UserName = Field(description='The arbitrary username given to the user.')
    client_id: str = Field(description='The client ID to use for the OAuth requests')
    client_secret: str = Field(description='The client secret to use for the OAuth requests')


class OAuthClientCredentialsPreset(BasePreset):
    type: Literal['oauth_client_credentials'] = 'oauth_client_credentials'

    url: str = Field(description='The URL of the token endpoint of the OpenIDConnect server')

    users: Sequence[OAuthClientCredentialsUserPreset] = Field(
        description='A list of users to create',
    )

    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        generate_token = ProcedureConfiguration(
            name=ProcedureName(self.slug),
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
                        url=self.url,
                        method=HTTPMethod.POST,
                        headers=[
                            HTTPHeader(name='Content-Type', values=[HTTPEncoding.FORM]),
                            HTTPHeader(name='Accept', values=[HTTPEncoding.JSON]),
                        ],
                        body=(
                            'grant_type=client_credentials'
                            '&client_id={{ client_id }}'
                            '&client_secret={{ client_secret }}'
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

        refresh_token = ProcedureConfiguration(
            name=ProcedureName(self.slug + '-refresh'),
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
                        url=self.url,
                        method=HTTPMethod.POST,
                        headers=[
                            HTTPHeader(name='Content-Type', values=['application/x-www-form-urlencoded']),
                            HTTPHeader(name='Accept', values=['application/json']),
                        ],
                        body=(
                            'grant_type=refresh_token&refresh_token={{ refresh_token }}'
                            '&client_id={{ client_id }}'
                            '&client_secret={{ client_secret }}'
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

        return [generate_token, refresh_token]

    def to_users(self) -> list[User]:
        return [
            User(
                name=user.username,
                variables=[
                    AuthenticationVariable(name=VariableName('client_id'), value=user.client_id),
                    AuthenticationVariable(name=VariableName('client_secret'), value=user.client_secret),
                ],
                procedure=self.slug,
                refresh=UserRefresh(procedure=ProcedureName(self.slug + '-refresh')),
            )
            for user in self.users
        ]
