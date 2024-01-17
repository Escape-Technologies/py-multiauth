from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import UserName
from multiauth.lib.http_core.entities import HTTPHeader
from multiauth.lib.presets.base import BasePreset, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.store.user import Credentials, User


class HeadersUserPreset(BaseUserPreset):
    username: UserName = Field(
        default=None,
        description='The name of the user. By default, the username is used.',
    )
    headers: dict[str, str] = Field(description='The headers of the user.')


def build_headers(user: HeadersUserPreset) -> list[HTTPHeader]:
    return [HTTPHeader(name=k, values=[v]) for k, v in user.headers.items()]


class HeadersPreset(BasePreset):
    type: Literal['headers'] = 'headers'

    users: Sequence[HeadersUserPreset] = Field(
        description='A list of users with basic credentials to create',
    )

    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        return []

    def to_users(self) -> list[User]:
        res: list[User] = []

        for user in self.users:
            res.append(
                User(
                    name=user.username,
                    credentials=Credentials(headers=build_headers(user)),
                ),
            )

        return res
