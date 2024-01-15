from http import HTTPMethod
from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.http_core.entities import HTTPEncoding, HTTPHeader, HTTPLocation
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, HTTPRequestParameters
from multiauth.lib.presets.basic import BasicUserPreset
from multiauth.lib.presets.cognito_base import AWSRegion
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRunnerConfiguration, TokenExtraction
from multiauth.lib.store.user import User, UserRefresh
from multiauth.lib.store.variables import AuthenticationVariable

###########################
###### AWS Password ######
###########################


class OAuthUserpassPreset(BasePreset):
    type: Literal['cognito_userpass'] = 'cognito_userpass'

    region: AWSRegion = Field(description='The region of the Cognito Service.')

    client_id: str = Field(description='The client ID to use for the OAuth requests')
    client_secret: str = Field(description='The client secret to use for the OAuth requests')

    users: Sequence[BasicUserPreset] = Field(description='A list of users to create')

    def to_procedure_configuration(self) -> list[ProcedureConfiguration]:
        generate_token = ProcedureConfiguration(
            name=ProcedureName(self.slug),
            injections=[
                TokenInjection(
                    location=HTTPLocation.HEADER,
                    key='Authorization',
                    prefix='Bearer ',
                    variable=VariableName('AccessToken'),
                ),
            ],
            operations=[
                HTTPRunnerConfiguration(
                    parameters=HTTPRequestParameters(
                        url=f'https://cognito-idp.{self.region}.amazonaws.com/',
                        method=HTTPMethod.POST,
                        headers=[
                            HTTPHeader(name='X-Amz-Target', values=['AWSCognitoIdentityProviderService.InitiateAuth']),
                            HTTPHeader(name='Content-Type', values=[HTTPEncoding.AWS_JSON]),
                        ],
                        body={
                            {
                                'AuthParameters': {
                                    'USERNAME': '{{ username }}',
                                    'PASSWORD': '{{ password }}',
                                    'SECRET_HASH': self.client_secret,
                                },
                                'AuthFlow': 'USER_PASSWORD_AUTH',
                                'ClientId': self.client_id,
                            },
                        },
                    ),
                    extractions=[
                        TokenExtraction(
                            location=HTTPLocation.BODY,
                            name=VariableName('AccessToken'),
                            key='AccessToken',
                        ),
                        TokenExtraction(
                            location=HTTPLocation.BODY,
                            name=VariableName('RefreshToken'),
                            key='RefreshToken',
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
                        url=f'https://cognito-idp.{self.region}.amazonaws.com/',
                        method=HTTPMethod.POST,
                        headers=[
                            HTTPHeader(name='X-Amz-Target', values=['AWSCognitoIdentityProviderService.InitiateAuth']),
                            HTTPHeader(name='Content-Type', values=[HTTPEncoding.AWS_JSON]),
                        ],
                        body={
                            {
                                'AuthParameters': {
                                    'REFRESH_TOKEN': '{{ RefreshToken }}',
                                    'SECRET_HASH': self.client_secret,
                                },
                                'AuthFlow': 'REFRESH_TOKEN_AUTH',
                                'ClientId': self.client_id,
                            },
                        },
                    ),
                    extractions=[
                        TokenExtraction(
                            location=HTTPLocation.BODY,
                            name=VariableName('AccessToken'),
                            key='AccessToken',
                        ),
                    ],
                ),
            ],
        )

        return [generate_token, refresh_token]

    def to_users(self) -> list[User]:
        return [
            User(
                name=UserName(user.name),
                variables=[
                    AuthenticationVariable(name=VariableName('username'), value=user.username),
                    AuthenticationVariable(name=VariableName('password'), value=user.password),
                ],
                procedure=self.slug,
                refresh=UserRefresh(procedure=ProcedureName(self.slug + '-refresh')),
            )
            for user in self.users
        ]
