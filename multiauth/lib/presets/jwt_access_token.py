from typing import Literal

from pydantic import Field

from multiauth.lib.entities import ProcedureName, VariableName
from multiauth.lib.http_core.entities import HTTPLocation
from multiauth.lib.presets.base import BasePreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction


class JWTAccessTokenRefreshTokenPreset(BasePreset):
    type: Literal['jwt_access_token_refresh_token'] = 'jwt_access_token_refresh_token'
    parameters: HTTPRequestParameters = Field(
        description=('The parameters of the HTTP request used to fetch the access and refresh tokens.'),
        examples=HTTPRequestParameters.examples(),
    )

    def to_procedure_configuration(self) -> ProcedureConfiguration:
        return ProcedureConfiguration(
            name=ProcedureName(self.name),
            operations=[
                HTTPRunnerConfiguration(
                    parameters=self.parameters,
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
