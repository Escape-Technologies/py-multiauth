from typing import Annotated, Union

from pydantic import BaseModel, Field

from multiauth.lib.presets.jwt_access_token import JWTAccessTokenRefreshTokenPreset
from multiauth.lib.presets.oauth_client_credentials import OAuthClientCredentialsPreset
from multiauth.lib.presets.oauth_refresh import OAuthRefreshPreset
from multiauth.lib.presets.oauth_userpass import OAuthUserpassPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.store.user import User

PresetType = Annotated[
    Union[JWTAccessTokenRefreshTokenPreset, OAuthUserpassPreset, OAuthClientCredentialsPreset, OAuthRefreshPreset],
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
    users: list[User] = Field(
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
