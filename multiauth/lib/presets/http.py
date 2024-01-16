from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction
from multiauth.lib.store.user import Credentials, User

VARIABLE_NAME = VariableName('token')


class HTTPUserPreset(BaseUserPreset, Credentials):
    username: UserName = Field(
        default=None,
        description='The username to attach to the HTTP requests sent for this user. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url',
        examples=['john'],
    )


class HTTPPreset(BasePreset):
    type: Literal['http'] = 'http'
    request: HTTPRequestParameters = Field(
        description=('The parameters of the HTTP request used to fetch the access and refresh tokens.'),
        examples=HTTPRequestParameters.examples(),
    )
    extract: TokenExtraction = Field(
        description='The token extraction configuration used to extract the tokens from the HTTP response.',
        examples=TokenExtraction.examples(),
    )
    inject: TokenInjection = Field(
        description='The injection configuration used to inject the tokens into the HTTP requests.',
        examples=TokenInjection.examples(),
    )

    users: Sequence[HTTPUserPreset] = Field(
        description='The list of users to generate tokens for.',
    )

    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        return [
            ProcedureConfiguration(
                name=ProcedureName(self.slug),
                injections=[
                    TokenInjection(
                        location=self.inject.location,
                        key=self.inject.key,
                        prefix=self.inject.prefix,
                        variable=VariableName(VARIABLE_NAME),
                    ),
                ],
                operations=[
                    HTTPRunnerConfiguration(
                        parameters=HTTPRequestParameters(
                            url=self.request.url,
                            method=self.request.method,
                            headers=self.request.headers,
                            cookies=self.request.cookies,
                            body=self.request.body,
                            query_parameters=self.request.query_parameters,
                            proxy=self.request.proxy,
                        ),
                        extractions=[
                            TokenExtraction(
                                location=self.extract.location,
                                name=VariableName(VARIABLE_NAME),
                                key=self.extract.key,
                                regex=self.extract.regex,
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def to_users(self) -> list[User]:
        return [
            User(
                name=user.username,
                credentials=Credentials(
                    username=user.username,
                    password=user.password,
                    headers=user.headers,
                    cookies=user.cookies,
                    body=user.body,
                    query_parameters=user.query_parameters,
                ),
                procedure=self.slug,
            )
            for user in self.users
        ]
