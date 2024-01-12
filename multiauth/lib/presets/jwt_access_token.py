from typing import Literal

from pydantic import Field

from multiauth.lib.presets.base import BasePreset
from multiauth.lib.procedure import ProcedureConfiguration, ProcedureName
from multiauth.lib.runners.http import HTTPBodyExtraction, HTTPRequestParameters, HTTPRunnerConfiguration
from multiauth.lib.store.variables import VariableName


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
                        HTTPBodyExtraction(
                            name=VariableName('access_token'),
                            key='access_token',
                        ),
                        HTTPBodyExtraction(
                            name=VariableName('refresh_token'),
                            key='refresh_token',
                        ),
                    ],
                ),
            ],
        )
