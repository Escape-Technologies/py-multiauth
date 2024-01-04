from typing import Literal

from multiauth.revamp.lib.presets.base import BasePreset
from multiauth.revamp.lib.procedure import ProcedureConfiguration, ProcedureName
from multiauth.revamp.lib.runners.http import HTTPBodyExtraction, HTTPRequestParameters, HTTPRunnerConfiguration
from multiauth.revamp.lib.store.variables import VariableName


class JWTAccessTokenRefreshTokenPreset(BasePreset):
    type: Literal['jwt_access_token_refresh_token'] = 'jwt_access_token_refresh_token'
    parameters: HTTPRequestParameters

    def to_procedure_configuration(self) -> ProcedureConfiguration:
        return ProcedureConfiguration(
            name=ProcedureName(self.name),
            requests=[
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
