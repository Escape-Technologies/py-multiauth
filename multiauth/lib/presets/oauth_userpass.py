from http import HTTPMethod
from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.http_core.entities import HTTPHeader, HTTPLocation
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction
from multiauth.lib.store.user import User, UserRefresh
from multiauth.lib.store.variables import AuthenticationVariable


class OAuthUserpassUserPreset(BaseUserPreset):
    password: str = Field(description='The password of the user.')


class OAuthUserpassPreset(BasePreset):
    type: Literal['oauth_userpass'] = 'oauth_userpass'

    url: str = Field(description='The URL of the token endpoint of the OpenIDConnect server')

    client_id: str = Field(description='The client ID to use for the OAuth requests')
    client_secret: str = Field(description='The client secret to use for the OAuth requests')

    users: Sequence[OAuthUserpassUserPreset] = Field(description='A list of users to create')

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
                            HTTPHeader(name='Content-Type', values=['application/x-www-form-urlencoded']),
                            HTTPHeader(name='Accept', values=['application/json']),
                        ],
                        body=(
                            'grant_type=password&username={{ username }}&password={{ password }}'
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
                        TokenExtraction(
                            location=HTTPLocation.BODY,
                            name=VariableName('refresh_token'),
                            key='refresh_token',
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

        return [generate_token, refresh_token]

    def to_users(self) -> list[User]:
        return [
            User(
                name=UserName(user.username),
                variables=[
                    AuthenticationVariable(name=VariableName('username'), value=user.username),
                    AuthenticationVariable(name=VariableName('password'), value=user.password),
                ],
                procedure=self.slug,
                refresh=UserRefresh(procedure=ProcedureName(self.slug + '-refresh')),
            )
            for user in self.users
        ]
