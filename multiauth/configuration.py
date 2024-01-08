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

    procedures: list[ProcedureConfiguration] = Field(
        default_factory=list,
        description='The list of authentication procedures to use',
    )
    presets: list[PresetType] = Field(default_factory=list, description='The list of presets to use')
    users: list[User] = Field(default_factory=list, description='List of users that can be used in procedures')
