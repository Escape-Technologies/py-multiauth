from typing import Annotated, Union

from pydantic import Field

from multiauth.helpers.base_model import StrictBaseModel
from multiauth.lib.presets.basic import BasicPreset
from multiauth.lib.presets.cognito_userpass import CognitoUserpassPreset
from multiauth.lib.presets.curl import cURLPreset
from multiauth.lib.presets.digest import DigestPreset
from multiauth.lib.presets.graphql import GraphQLPreset
from multiauth.lib.presets.headers import HeadersPreset
from multiauth.lib.presets.http import HTTPPreset
from multiauth.lib.presets.oauth_client_credentials import OAuthClientCredentialsPreset
from multiauth.lib.presets.oauth_userpass import OAuthUserpassPreset
from multiauth.lib.presets.webdriver import WebdriverPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.store.user import User

PresetType = Annotated[
    Union[
        HTTPPreset,
        OAuthUserpassPreset,
        OAuthClientCredentialsPreset,
        BasicPreset,
        GraphQLPreset,
        DigestPreset,
        CognitoUserpassPreset,
        HeadersPreset,
        cURLPreset,
        WebdriverPreset,
    ],
    Field(discriminator='type'),
]


class MultiauthConfiguration(StrictBaseModel):
    """
    Multiauth configuration model.
    """

    schema_: str | None = Field(default=None, alias='$schema', description='The schema of the configuration file')

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

    def expand(self) -> 'MultiauthConfiguration':
        """
        Expand the configuration by generating procedures and users from presets.
        """

        if self.presets is None:
            return self

        procedures = self.procedures or []
        users = self.users or []

        for preset in self.presets:
            for procedure in preset.to_procedure_configurations():
                procedures.append(procedure)
            for user in preset.to_users():
                users.append(user)

        return MultiauthConfiguration(
            procedures=procedures,
            presets=None,
            users=users,
            proxy=self.proxy,
        )

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
