from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.http_core.curl import parse_curl
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction
from multiauth.lib.store.user import Credentials, User


class HTTPUserPreset(BaseUserPreset, Credentials):
    name: UserName = Field(description='The arbitrary name that identifies the user.')
    curl: str = Field(description='The curl command that is used to fetch the tokens for this user.')

    @property
    def identifier(self) -> UserName:
        return self.name


VARIABLE_NAME = 'token'


class HTTPPreset(BasePreset):
    type: Literal['http'] = 'http'

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
        procedures = list[ProcedureConfiguration]()

        for user in self.users:
            request = parse_curl(user.curl)
            procedures.append(
                ProcedureConfiguration(
                    name=ProcedureName(self.slug + user.identifier),
                    injections=[
                        TokenInjection(
                            location=self.inject.location,
                            key=self.inject.key,
                            prefix=self.inject.prefix,
                            variable=VariableName(f'{user.identifier}-{VARIABLE_NAME}'),
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
                                    name=VariableName(f'{user.identifier}-{VARIABLE_NAME}'),
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
                name=user.identifier,
                procedure=ProcedureName(self.slug + user.identifier),
            )
            for user in self.users
        ]
