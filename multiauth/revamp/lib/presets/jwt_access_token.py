from typing import Literal

from multiauth.revamp.lib.presets.base import BasePreset
from multiauth.revamp.lib.procedure import ProcedureConfiguration
from multiauth.revamp.lib.runners.http import HTTPBodyExtraction, HTTPRequestConfiguration, HTTPRequestParameters


class JWTAccessTokenRefreshTokenPreset(BasePreset):
    type: Literal['jwt_access_token_refresh_token'] = 'jwt_access_token_refresh_token'
    parameters: HTTPRequestParameters

    def to_procedure_configuration(self) -> ProcedureConfiguration:
        return ProcedureConfiguration(
            name=self.name,
            requests=[
                HTTPRequestConfiguration(
                    parameters=self.parameters,
                    extractions=[
                        HTTPBodyExtraction(
                            name='access_token',
                            key='access_token',
                        ),
                        HTTPBodyExtraction(
                            name='refresh_token',
                            key='refresh_token',
                        ),
                    ],
                ),
            ],
        )
