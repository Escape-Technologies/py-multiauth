from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.http_core.curl import parse_curl
from multiauth.lib.http_core.entities import HTTPLocation
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, BasePresetDoc, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction
from multiauth.lib.store.user import Credentials, User


class cURLUserPreset(BaseUserPreset, Credentials):
    username: UserName = Field(description='The arbitrary name that identifies the user.')
    curl: str = Field(description='The curl command that is used to fetch the tokens for this user.')


VARIABLE_NAME = 'token'


class cURLPreset(BasePreset):
    type: Literal['curl'] = 'curl'

    extract: TokenExtraction = Field(
        description='The token extraction configuration used to extract the tokens from the HTTP response.',
        examples=TokenExtraction.examples(),
    )
    inject: TokenInjection = Field(
        description='The injection configuration used to inject the tokens into the HTTP requests.',
        examples=TokenInjection.examples(),
    )

    users: Sequence[cURLUserPreset] = Field(
        description='The list of users to generate tokens for.',
    )

    @staticmethod
    def _doc() -> BasePresetDoc:
        return BasePresetDoc(
            title='cURL',
            description="""The 'cURL' authentication preset is designed for dynamic token generation and reuse:

- **cURL Command Parsing**: Parses a cURL command to send an authentication request.
- **Dynamic Token Extraction**: Extracts the authentication token from the cURL command's HTTP response.
- **Token Re-injection**: Reinjects the extracted token into subsequent authenticated requests.

This preset is particularly useful for scenarios where authentication tokens are dynamically generated and need to be efficiently extracted and reused in ongoing requests.

Two common use cases are:
- **Bearer JWT Token**: A REST API request that generates a Bearer JWT Token, which is then reinjected into the Authorization header for subsequent requests.
- **Set-Cookie**: A REST API request that generates a cookie, which is then set in the cookies for subsequent requests.""",  # noqa: E501
            examples=[
                cURLPreset(
                    type='curl',
                    extract=TokenExtraction(
                        location=HTTPLocation.HEADER,
                        key='Authorization',
                    ),
                    inject=TokenInjection(
                        location=HTTPLocation.HEADER,
                        key='Authorization',
                        prefix='Bearer',
                    ),
                    users=[
                        cURLUserPreset(
                            username=UserName('user1'),
                            curl='curl -X POST https://api.example.com/auth -d "username=user1&password=pass1"',
                        ),
                    ],
                ),
                cURLPreset(
                    type='curl',
                    extract=TokenExtraction(
                        location=HTTPLocation.HEADER,
                        key='Set-Cookie',
                        regex=r'session_id=(\S+);',
                    ),
                    inject=TokenInjection(
                        location=HTTPLocation.COOKIE,
                        key='session_id',
                        variable='sessionId',
                    ),
                    users=[
                        cURLUserPreset(
                            username=UserName('user2'),
                            curl='curl -X POST https://api.example.com/login -d "username=user2&password=pass2"',
                        ),
                    ],
                ),
            ],
        )

    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        procedures = list[ProcedureConfiguration]()

        for user in self.users:
            request = parse_curl(user.curl)
            procedures.append(
                ProcedureConfiguration(
                    name=ProcedureName(self.slug + user.username),
                    injections=[
                        TokenInjection(
                            location=self.inject.location,
                            key=self.inject.key,
                            prefix=self.inject.prefix,
                            variable=VariableName(f'{user.username}-{VARIABLE_NAME}'),
                        ),
                    ],
                    operations=[
                        HTTPRunnerConfiguration(
                            parameters=HTTPRequestParameters(
                                url=request.url,
                                method=request.method,
                                headers=request.headers,
                                cookies=request.cookies,
                                body=request.data_text,
                                query_parameters=request.query_parameters,
                                proxy=request.proxy,
                            ),
                            extractions=[
                                TokenExtraction(
                                    location=self.extract.location,
                                    name=VariableName(f'{user.username}-{VARIABLE_NAME}'),
                                    key=self.extract.key,
                                    regex=self.extract.regex,
                                ),
                            ],
                        ),
                    ],
                ),
            )

        return procedures

    def to_users(self) -> list[User]:
        return [
            User(
                name=user.username,
                procedure=ProcedureName(self.slug + user.username),
            )
            for user in self.users
        ]
