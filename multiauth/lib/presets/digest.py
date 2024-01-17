from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName
from multiauth.lib.presets.base import BasePreset
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
                ),
            )
            for user in self.users
        ]
