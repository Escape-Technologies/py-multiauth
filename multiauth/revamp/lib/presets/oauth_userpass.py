from http import HTTPMethod
from typing import Literal

from multiauth.entities.user import ProcedureName
from multiauth.revamp.lib.http_core.entities import HTTPHeader
from multiauth.revamp.lib.presets.base import BasePreset
from multiauth.revamp.lib.procedure import ProcedureConfiguration
from multiauth.revamp.lib.runners.http import HTTPBodyExtraction, HTTPRequestConfiguration, HTTPRequestParameters
from multiauth.revamp.lib.store.variables import VariableName


class OAuthUserpassPreset(BasePreset):
    type: Literal['oauth_userpass'] = 'oauth_userpass'

    server_url: str

    client_id: str
    client_secret: str
    username: str
    password: str

    def to_procedure_configuration(self) -> ProcedureConfiguration:
        return ProcedureConfiguration(
            name=ProcedureName(self.name),
            requests=[
                HTTPRequestConfiguration(
                    parameters=HTTPRequestParameters(
                        url=self.server_url,
                        method=HTTPMethod.POST,
                        headers=[
                            HTTPHeader(name='Content-Type', values=['application/x-www-form-urlencoded']),
                            HTTPHeader(name='Accept', values=['application/json']),
                        ],
                        body={
                            'grant_type': 'password',
                            'client_id': self.client_id,
                            'client_secret': self.client_secret,
                            'username': self.username,
                            'password': self.password,
                        },
                    ),
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
