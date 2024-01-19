import base64
from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import UserName
from multiauth.lib.http_core.entities import HTTPCookie, HTTPHeader
from multiauth.lib.presets.base import BasePreset, BasePresetDoc, BaseUserPreset
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

    @staticmethod
    def _doc() -> BasePresetDoc:
        return BasePresetDoc(
            title='Basic',
            description="""The 'Basic' authentication preset is designed for straightforward authentication scenarios:

- **Credentials Encoding**: User's credentials (username and password) are encoded in **base64**.
- **Header Attachment**: The encoded credentials are attached to the request headers.
- **Authorization Header**: The client sends these credentials in the **Authorization** header of the HTTP request.

This method provides a simple and direct way to authenticate users, without requiring additional server requests for user creation or authentication. It is best suited for scenarios where simplicity and ease of implementation are prioritized.

**Note**: While this method is straightforward, it's less secure compared to more advanced authentication methods.""",  # noqa: E501
            examples=[
                BasicPreset(
                    type='basic',
                    users=[
                        BasicUserPreset(username=UserName('user1'), password='pass1'),  # noqa: S106
                        BasicUserPreset(username=UserName('user2'), password='pass2'),  # noqa: S106
                    ],
                ),
            ],
        )

    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        return []

    def to_users(self) -> list[User]:
        res: list[User] = []

        for user in self.users:
            basic_headers = [build_basic_headers(user.username, user.password)]
            headers = HTTPHeader.merge(HTTPHeader.from_dict(user.headers) + basic_headers)
            res.append(
                User(
                    name=UserName(user.username),
                    credentials=Credentials(headers=headers, cookies=HTTPCookie.from_dict(user.cookies)),
                ),
            )

        return res
