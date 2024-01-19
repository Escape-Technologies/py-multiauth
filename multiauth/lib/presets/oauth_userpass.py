from http import HTTPMethod
from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.http_core.entities import HTTPHeader, HTTPLocation
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, BasePresetDoc, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction
from multiauth.lib.store.user import User, UserRefresh
from multiauth.lib.store.variables import AuthenticationVariable


class OAuthUserpassUserPreset(BaseUserPreset):
    password: str = Field(description='The password of the user.')
    scopes: list[str] | None = Field(
        default=None,
        description='A list of scopes to request for the user. If not specified, no scopes will be requested.',
    )


class OAuthUserpassPreset(BasePreset):
    type: Literal['oauth_userpass'] = 'oauth_userpass'

    url: str = Field(description='The URL of the token endpoint of the OpenIDConnect server')

    client_id: str = Field(description='The client ID to use for the OAuth requests')
    client_secret: str = Field(description='The client secret to use for the OAuth requests')

    users: Sequence[OAuthUserpassUserPreset] = Field(description='A list of users to create')

    @staticmethod
    def _doc() -> BasePresetDoc:
        return BasePresetDoc(
            title='OAuth User Password',
            description="""The 'OAuth User Password' preset is designed for authentication using the OAuth 2.0 framework with user password credentials:

- **OAuth Token Endpoint**: Authentication requests are sent to the specified OAuth token endpoint of an OpenID Connect server.
- **Client Credentials**: Includes the client ID and client secret for authenticating the OAuth request.
- **User Password Credentials**: This preset supports the OAuth password grant type, using individual user passwords for token generation.

This method is suitable for systems that require secure, OAuth-based authentication with user credentials, especially in scenarios where direct user-password-based authentication is preferred.""",  # noqa: E501
            examples=[
                OAuthUserpassPreset(
                    type='oauth_userpass',
                    url='https://oauth.example.com/token',
                    client_id='client123',
                    client_secret='secretXYZ',  # noqa: S106
                    users=[
                        OAuthUserpassUserPreset(username=UserName('user1'), password='pass1'),  # noqa: S106
                        OAuthUserpassUserPreset(username=UserName('user2'), password='pass2'),  # noqa: S106
                        OAuthUserpassUserPreset(
                            username=UserName('user3'),
                            password='pass3',  # noqa: S106
                            scopes=['create', 'delete'],
                        ),
                    ],
                ),
            ],
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
                            HTTPHeader(name='Content-Type', values=['application/x-www-form-urlencoded']),
                            HTTPHeader(name='Accept', values=['application/json']),
                        ],
                        body=(
                            'grant_type=password&username={{ username }}&password={{ password }}'
                            '&scope={{ scope }}'
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
                            '&scope={{ scope }}'
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
                    AuthenticationVariable(name=VariableName('scope'), value='+'.join(user.scopes or [])),
                ],
                procedure=self.slug,
                refresh=UserRefresh(procedure=ProcedureName(self.slug + '-refresh')),
            )
            for user in self.users
        ]
