import base64
from http import HTTPMethod
from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName
from multiauth.lib.http_core.entities import HTTPEncoding, HTTPHeader
from multiauth.lib.presets.base import BasePreset, UserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration
from multiauth.lib.store.user import User


def build_basic_headers(username: str, password: str) -> HTTPHeader:
    value = 'Basic ' + base64.b64encode(f'{username}:{password}'.encode()).decode()
    return HTTPHeader(name='Authorization', values=[value])


class BasicUserPreset(UserPreset):
    username: str = Field(description='The Basic username of the user.')
    password: str = Field(description='The Basic password of the user.')


class BasicBasePreset(BasePreset):
    type: Literal['basic'] = 'basic'

    url: str = Field(description='The URL of the Basic authentication endpoint.')

    users: Sequence[BasicUserPreset] = Field(
        description='A list of users with basic credentials to create',
    )

    def to_procedure_configuration(self) -> ProcedureConfiguration:
        return ProcedureConfiguration(
            name=ProcedureName(self.name),
            operations=[
                HTTPRunnerConfiguration(
                    parameters=HTTPRequestParameters(
                        url=self.url,
                        method=HTTPMethod.POST,
                        headers=[
                            HTTPHeader(name='Accept', values=[HTTPEncoding.JSON]),
                        ],
                    ),
                ),
            ],
        )

    def to_users(self) -> list[User]:
        res: list[User] = []

        for user in self.users:
            creds = user.to_credentials()
            creds.headers += [build_basic_headers(user.username, user.password)]
            res.append(
                User(
                    name=UserName(user.name),
                    credentials=creds,
                    procedure=ProcedureName(self.name),
                ),
            )

        return res
