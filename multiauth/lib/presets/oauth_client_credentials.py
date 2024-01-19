from http import HTTPMethod
from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.http_core.entities import HTTPCookie, HTTPEncoding, HTTPHeader, HTTPLocation
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, BasePresetDoc, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction
from multiauth.lib.store.user import Credentials, User, UserRefresh
from multiauth.lib.store.variables import AuthenticationVariable


class OAuthClientCredentialsUserPreset(BaseUserPreset):
    username: UserName = Field(description='The arbitrary username given to the user.')
    client_id: str = Field(description='The client ID to use for the OAuth requests')
    client_secret: str = Field(description='The client secret to use for the OAuth requests')
    scopes: list[str] | None = Field(
        default=None,
        description='A list of scopes to request for the user. If not specified, no scopes will be requested.',
    )


class OAuthClientCredentialsPreset(BasePreset):
    type: Literal['oauth_client_credentials'] = 'oauth_client_credentials'

    url: str = Field(description='The URL of the token endpoint of the OpenIDConnect server')
    users: Sequence[OAuthClientCredentialsUserPreset] = Field(
        description='A list of users to create',
    )

    @staticmethod
    def _doc() -> BasePresetDoc:
        return BasePresetDoc(
            title='OAuth Client Credentials',
            description="""The 'OAuth Client Credentials' preset is tailored for authentication using the OAuth 2.0 client credentials grant, ideal for service accounts:

- **OAuth Token Endpoint**: Directs authentication requests to the token endpoint of an OpenID Connect server.
- **Service Account Credentials**: Utilizes client IDs and secrets to authenticate, representing service accounts rather than individual end-users.
- **Token Generation**: Designed to obtain access tokens for service accounts without the need for a user's password.

This preset is particularly effective for scenarios where applications or services themselves need to authenticate, independent of a user's direct involvement.""",  # noqa: E501
            examples=[
                OAuthClientCredentialsPreset(
                    type='oauth_client_credentials',
                    url='https://oauth.example.com/token',
                    users=[
                        OAuthClientCredentialsUserPreset(
                            username=UserName('serviceAccount1'),
                            client_id='serviceClientID1',
                            client_secret='serviceSecret1',  # noqa: S106
                        ),
                        OAuthClientCredentialsUserPreset(
                            username=UserName('serviceAccount2'),
                            scopes=['create', 'delete'],
                            client_id='serviceClientID2',
                            client_secret='serviceSecret2',  # noqa: S106
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
                            HTTPHeader(name='Content-Type', values=[HTTPEncoding.FORM]),
                            HTTPHeader(name='Accept', values=[HTTPEncoding.JSON]),
                        ],
                        body=(
                            'grant_type=client_credentials'
                            '&client_id={{ client_id }}'
                            '&client_secret={{ client_secret }}'
                            '&scope={{ scope }}'
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
                            '&scope={{ scope }}'
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
                    AuthenticationVariable(name=VariableName('scope'), value='+'.join(user.scopes or [])),
                ],
                procedure=self.slug,
                refresh=UserRefresh(procedure=ProcedureName(self.slug + '-refresh')),
                credentials=Credentials(
                    headers=HTTPHeader.from_dict(user.headers),
                    cookies=HTTPCookie.from_dict(user.cookies),
                ),
            )
            for user in self.users
        ]
