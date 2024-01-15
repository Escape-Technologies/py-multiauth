from typing import Literal, Sequence

from pydantic import Field, root_validator

from multiauth.lib.entities import ProcedureName, VariableName
from multiauth.lib.extraction import BaseExtraction
from multiauth.lib.injection import BaseInjection, TokenInjection
from multiauth.lib.presets.base import BasePreset, UserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction
from multiauth.lib.store.user import Credentials, User

VARIABLE_NAME = VariableName('token')


class RESTUserPreset(UserPreset, Credentials):
    @root_validator(pre=True)
    def default_name(cls, values: dict) -> dict:
        name, username = values.get('name'), values.get('username')
        if name is None and username is not None:
            values['name'] = username
        return values


class HTTPPreset(BasePreset):
    type: Literal['http'] = 'http'
    request: HTTPRequestParameters = Field(
        description=('The parameters of the HTTP request used to fetch the access and refresh tokens.'),
        examples=HTTPRequestParameters.examples(),
    )
    extract: BaseExtraction = Field(
        description='The token extraction configuration used to extract the tokens from the HTTP response.',
        examples=TokenExtraction.examples(),
    )
    inject: BaseInjection = Field(
        description='The injection configuration used to inject the tokens into the HTTP requests.',
        examples=TokenExtraction.examples(),
    )

    users: Sequence[RESTUserPreset] = Field(
        description='The list of users to generate tokens for.',
    )

    def to_procedure_configuration(self) -> list[ProcedureConfiguration]:
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
                name=user.name,
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
