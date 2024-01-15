from typing import Literal

from pydantic import Field

from multiauth.lib.entities import ProcedureName, VariableName
from multiauth.lib.extraction import BaseExtraction
from multiauth.lib.injection import BaseInjection, TokenInjection
from multiauth.lib.presets.base import BasePreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction

VARIABLE_NAME = VariableName('token')


class RESTPreset(BasePreset):
    type: Literal['jwt'] = 'jwt'
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

    def to_procedure_configuration(self) -> ProcedureConfiguration:
        return ProcedureConfiguration(
            name=ProcedureName(self.name),
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
        )
