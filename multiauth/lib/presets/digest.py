from http import HTTPMethod
from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName
from multiauth.lib.http_core.entities import HTTPCookie, HTTPHeader
from multiauth.lib.presets.base import BasePreset, BasePresetDoc
from multiauth.lib.presets.basic import BasicUserPreset
from multiauth.lib.presets.http import HTTPRequestPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.digest import (
    DigestRequestSequenceConfiguration,
    DigestRunnerConfiguration,
    DigestSecondRequestConfiguration,
)
from multiauth.lib.runners.http import HTTPRequestParameters
from multiauth.lib.store.user import Credentials, User


class DigestPreset(BasePreset):
    type: Literal['digest'] = 'digest'

    first_request: HTTPRequestPreset = Field(
        description=(
            'The parameters of the first HTTP request executed during the digest procedure.'
            'It is the one that returns the WWW-Authenticate header.'
        ),
        examples=HTTPRequestParameters.examples(),
    )
    second_request: DigestSecondRequestConfiguration | None = Field(
        default=None,
        description=(
            'The parameters of the second HTTP request executed during the digest procedure.'
            'It is the one that uses the digest authentication. By default, parameters of the first request are used.'
        ),
        examples=DigestSecondRequestConfiguration.examples(),
    )

    users: Sequence[BasicUserPreset] = Field(
        description='The list of users to generate tokens for.',
    )

    @staticmethod
    def _doc() -> BasePresetDoc:
        return BasePresetDoc(
            title='Digest',
            description="""The 'Digest' authentication preset employs a challenge-response mechanism for enhanced security:

- **Initial Request**: Involves sending a request to a server endpoint that responds with a `WWW-Authenticate` header, initiating the authentication process.
- **Credentials Processing**: The client creates a hashed version of the user's credentials using the challenge details received.
- **Second Request**: The client sends a second request with this hashed information to authenticate.

This method enhances security by avoiding the transmission of actual passwords over the network.
Digest Authentication is suitable for scenarios requiring enhanced security without the complexities of more advanced authentication methods.""",  # noqa: E501
            examples=[
                DigestPreset(
                    type='digest',
                    first_request=HTTPRequestPreset(
                        url='https://api.example.com/request',
                        method=HTTPMethod.GET,
                        headers={'Accept': 'application/json'},
                        cookies={'session_id': '123456'},
                        query_parameters={'query': 'info'},
                    ),
                    second_request=DigestSecondRequestConfiguration(
                        url='https://api.example.com/authenticate',
                        method=HTTPMethod.POST,
                    ),
                    users=[
                        BasicUserPreset(username=UserName('alice'), password='aliceSecret'),  # noqa: S106
                        BasicUserPreset(username=UserName('bob'), password='bobSecret'),  # noqa: S106
                    ],
                ),
            ],
        )

    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        return [
            ProcedureConfiguration(
                name=ProcedureName(self.slug),
                operations=[
                    DigestRunnerConfiguration(
                        parameters=DigestRequestSequenceConfiguration(
                            first_request=self.first_request.to_std_http_parameters(),
                            second_request=self.second_request,
                        ),
                        extractions=[],
                    ),
                ],
            ),
        ]

    def to_users(self) -> list[User]:
        return [
            User(
                procedure=ProcedureName(self.slug),
                name=user.username,
                credentials=Credentials(
                    username=user.username,
                    password=user.password,
                    headers=HTTPHeader.from_dict(user.headers),
                    cookies=HTTPCookie.from_dict(user.cookies),
                ),
            )
            for user in self.users
        ]
