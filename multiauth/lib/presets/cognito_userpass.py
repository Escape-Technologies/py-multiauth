import enum
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

###########################
## Auth with cURL: https://stackoverflow.com/questions/58833462/aws-cognito-authentication-curl-call-generate-token-without-cli-no-clien
###########################


class AWSRegion(enum.StrEnum):
    US_EAST_OHIO = 'us-east-2'
    US_EAST_N_VIRGINIA = 'us-east-1'
    US_WEST_N_CALIFORNIA = 'us-west-1'
    US_WEST_OREGON = 'us-west-2'
    AFRICA_CAPE_TOWN = 'af-south-1'
    ASIA_PACIFIC_HONG_KONG = 'ap-east-1'
    ASIA_PACIFIC_MUMBAI = 'ap-south-1'
    ASIA_PACIFIC_OSAKA = 'ap-northeast-3'
    ASIA_PACIFIC_SEOUL = 'ap-northeast-2'
    ASIA_PACIFIC_SINGAPORE = 'ap-southeast-1'
    ASIA_PACIFIC_SYDNEY = 'ap-southeast-2'
    ASIA_PACIFIC_TOKYO = 'ap-northeast-1'
    CANADA_CENTRAL = 'ca-central-1'
    CHINA_BEIJING = 'cn-north-1'
    CHINA_NINGXIA = 'cn-northwest-1'
    EUROPE_FRANKFURT = 'eu-central-1'
    EUROPE_IRELAND = 'eu-west-1'
    EUROPE_LONDON = 'eu-west-2'
    EUROPE_MILAN = 'eu-south-1'
    EUROPE_PARIS = 'eu-west-3'
    EUROPE_STOCKHOLM = 'eu-north-1'
    MIDDLE_EAST_BAHRAIN = 'me-south-1'
    SOUTH_AMERICA_SAO_PAULO = 'sa-east-1'


###########################
###### AWS Password ######
###########################


class CognitoUserpassUserPreset(BaseUserPreset):
    username: UserName = Field(description='The username of the user.')
    password: str = Field(description='The password of the user.')
    scopes: list[str] | None = Field(
        default=None,
        description='A list of scopes to request for the user. If not specified, no scopes will be requested.',
    )


class CognitoUserpassPreset(BasePreset):
    type: Literal['cognito_userpass'] = 'cognito_userpass'

    region: AWSRegion = Field(description='The region of the Cognito Service.')

    client_id: str = Field(description='The client ID to use for the OAuth requests')
    client_secret: str = Field(description='The client secret to use for the OAuth requests')

    users: Sequence[CognitoUserpassUserPreset] = Field(description='A list of users to create')

    @staticmethod
    def _doc() -> BasePresetDoc:
        return BasePresetDoc(
            title='AWS Cognito',
            description="""The 'Cognito User Password' preset is designed for authentication using AWS Cognito with username and password credentials:

- **AWS Cognito Integration**: Leverages AWS Cognito, a comprehensive user identity and data synchronization service, for authentication.
- **Regional Configuration**: Allows specifying the AWS region where the Cognito service is hosted, ensuring proper routing and compliance with data residency requirements.
- **Client Credentials**: Utilizes a client ID and client secret for secure OAuth requests within the Cognito framework.
- **User Authentication**: Facilitates the creation and authentication of users with a username and password.

This preset is ideal for systems that use AWS Cognito for managing user authentication, providing a seamless integration with the AWS ecosystem.""",  # noqa: E501
            examples=[
                CognitoUserpassPreset(
                    type='cognito_userpass',
                    region=AWSRegion.US_WEST_N_CALIFORNIA,
                    client_id='yourCognitoClientId',
                    client_secret='yourCognitoClientSecret',  # noqa: S106
                    users=[
                        CognitoUserpassUserPreset(
                            username=UserName('user1'),
                            password='pass1',  # noqa: S106,
                            scopes=['create', 'delete'],
                        ),
                        CognitoUserpassUserPreset(username=UserName('user2'), password='pass2'),  # noqa: S106
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
                            'AuthParameters': {
                                'USERNAME': '{{ username }}',
                                'PASSWORD': '{{ password }}',
                                'SECRET_HASH': self.client_secret,
                            },
                            'AuthFlow': 'USER_PASSWORD_AUTH',
                            'ClientId': self.client_id,
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
                            'AuthParameters': {
                                'REFRESH_TOKEN': '{{ RefreshToken }}',
                                'SECRET_HASH': self.client_secret,
                            },
                            'AuthFlow': 'REFRESH_TOKEN_AUTH',
                            'ClientId': self.client_id,
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
                name=UserName(user.username),
                credentials=Credentials(
                    headers=HTTPHeader.from_dict(user.headers),
                    cookies=HTTPCookie.from_dict(user.cookies),
                ),
                variables=[
                    AuthenticationVariable(name=VariableName('username'), value=user.username),
                    AuthenticationVariable(name=VariableName('password'), value=user.password),
                ],
                procedure=self.slug,
                refresh=UserRefresh(procedure=ProcedureName(self.slug + '-refresh')),
            )
            for user in self.users
        ]
