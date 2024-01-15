import base64
from typing import Literal, Sequence

from pydantic import Field, root_validator

from multiauth.lib.entities import UserName
from multiauth.lib.http_core.entities import HTTPHeader
from multiauth.lib.presets.base import BasePreset, UserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.store.user import Credentials, User


def build_basic_headers(username: str, password: str) -> HTTPHeader:
    value = 'Basic ' + base64.b64encode(f'{username}:{password}'.encode()).decode()
    return HTTPHeader(name='Authorization', values=[value])


class BasicUserPreset(UserPreset):
    name: UserName = Field(
        default=None,
        description='The name of the user. By default, the username is used.',
    )
    username: str = Field(description='The Basic username of the user.')
    password: str = Field(description='The Basic password of the user.')

    @root_validator(pre=True)
    def default_name(cls, values: dict) -> dict:
        name, username = values.get('name'), values.get('username')
        if name is None and username is not None:
            values['name'] = username
        return values


class BasicPreset(BasePreset):
    type: Literal['basic'] = 'basic'

    users: Sequence[BasicUserPreset] = Field(
        description='A list of users with basic credentials to create',
    )

    def to_procedure_configuration(self) -> list[ProcedureConfiguration]:
        return []

    def to_users(self) -> list[User]:
        res: list[User] = []

        for user in self.users:
            res.append(
                User(
                    procedure=self.slug,
                    name=UserName(user.username),
                    credentials=Credentials(headers=[build_basic_headers(user.username, user.password)]),
                ),
            )

        return res
