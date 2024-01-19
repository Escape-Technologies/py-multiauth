from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import UserName
from multiauth.lib.http_core.entities import HTTPCookie, HTTPHeader
from multiauth.lib.presets.base import BasePreset, BasePresetDoc, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.store.user import Credentials, User


class HeadersUserPreset(BaseUserPreset):
    username: UserName = Field(description='The name of the user.')
    headers: dict[str, str] = Field(description='The headers of the user.')


def build_headers(user: HeadersUserPreset) -> list[HTTPHeader]:
    return [HTTPHeader(name=k, values=[v]) for k, v in user.headers.items()]


class HeadersPreset(BasePreset):
    type: Literal['headers'] = 'headers'

    users: Sequence[HeadersUserPreset] = Field(
        description='A list of users with basic credentials to create',
    )

    @staticmethod
    def _doc() -> BasePresetDoc:
        return BasePresetDoc(
            title='Headers',
            description="""The 'Headers' authentication preset is a straightforward, manual authentication method:

- **Manual Token Injection**: Authentication is achieved by manually injecting tokens or credentials into the request headers. No authentication request is necessary.
- **Static Credentials**: User credentials are static and defined in advance, making setup simple.
- **Token Expiry Consideration**: A key aspect to consider is that since tokens are manually set, they may expire, necessitating regular manual updates to maintain access.

This preset is ideal for scenarios where authentication can be handled via predefined headers, but users should be mindful of the need to regularly update tokens or credentials to avoid access issues.""",  # noqa: E501
            examples=[
                HeadersPreset(
                    type='headers',
                    users=[
                        HeadersUserPreset(username=UserName('user1'), headers={'Authorization': 'Bearer user1Token'}),
                        HeadersUserPreset(username=UserName('user2'), headers={'Authorization': 'Bearer user2Token'}),
                    ],
                ),
            ],
        )

    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        return []

    def to_users(self) -> list[User]:
        res: list[User] = []

        for user in self.users:
            built_headers = build_headers(user)
            headers = HTTPHeader.merge(HTTPHeader.from_dict(user.headers) + built_headers)

            res.append(
                User(
                    name=user.username,
                    credentials=Credentials(headers=headers, cookies=HTTPCookie.from_dict(user.cookies)),
                ),
            )

        return res
