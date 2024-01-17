import base64
from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import UserName
from multiauth.lib.http_core.entities import HTTPHeader
from multiauth.lib.presets.base import BasePreset, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.store.user import Credentials, User


def build_basic_headers(username: str, password: str) -> HTTPHeader:
    value = 'Basic ' + base64.b64encode(f'{username}:{password}'.encode()).decode()
    return HTTPHeader(name='Authorization', values=[value])


class BasicUserPreset(BaseUserPreset):
    username: UserName = Field(description='The Basic username of the user.')
    password: str = Field(description='The Basic password of the user.')


class BasicPreset(BasePreset):
    type: Literal['basic'] = 'basic'

    users: Sequence[BasicUserPreset] = Field(
        description='A list of users with basic credentials to create',
    )

    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        return []

    def to_users(self) -> list[User]:
        res: list[User] = []

        for user in self.users:
            res.append(
                User(
                    name=UserName(user.username),
                    credentials=Credentials(headers=[build_basic_headers(user.username, user.password)]),
                ),
            )

        return res
