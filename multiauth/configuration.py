from typing import Annotated, Union

from pydantic import BaseModel, Field

from multiauth.lib.presets.basic import BasicPreset
from multiauth.lib.presets.graphql import GraphQLPreset
from multiauth.lib.presets.http import HTTPPreset
from multiauth.lib.presets.oauth_client_credentials import OAuthClientCredentialsPreset
from multiauth.lib.presets.oauth_userpass import OAuthUserpassPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.store.user import User

PresetType = Annotated[
    Union[
        HTTPPreset,
        OAuthUserpassPreset,
        OAuthClientCredentialsPreset,
        BasicPreset,
        GraphQLPreset,
    ],
    Field(discriminator='type'),
]


class MultiauthConfiguration(BaseModel):
    """
    Multiauth configuration model.
    """

    procedures: list[ProcedureConfiguration] | None = Field(
        default=None,
        description='The list of authentication procedures to rely on when authenticating users',
    )
    presets: list[PresetType] | None = Field(
        default=None,
        description=(
            'A list of presets used to easily generate procedures and users automatically '
            'following common authentication standards'
        ),
    )
    users: list[User] | None = Field(
        default=None,
        description='List of users that multiauth will generate authentications for.',
    )
    proxy: str | None = Field(default=None, description='An eventual global proxy used for all HTTP requests')

    @staticmethod
    def public() -> 'MultiauthConfiguration':
        """
        Return a public configuration.
        """

        return MultiauthConfiguration(
            procedures=[],
            presets=[],
            users=[User.public()],
            proxy=None,
        )
