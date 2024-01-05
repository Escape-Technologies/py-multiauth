from typing import Annotated, Union

from pydantic import BaseModel, Field

from multiauth.revamp.lib.presets.jwt_access_token import JWTAccessTokenRefreshTokenPreset
from multiauth.revamp.lib.presets.oauth_client_credentials import OAuthClientCredentialsPreset
from multiauth.revamp.lib.presets.oauth_refresh import OAuthRefreshPreset
from multiauth.revamp.lib.presets.oauth_userpass import OAuthUserpassPreset
from multiauth.revamp.lib.procedure import ProcedureConfiguration
from multiauth.revamp.lib.store.user import User

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
