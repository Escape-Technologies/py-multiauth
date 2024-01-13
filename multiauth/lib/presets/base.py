import abc
from typing import Literal, Sequence

from pydantic import BaseModel, Field

from multiauth.lib.entities import ProcedureName, UserName
from multiauth.lib.extraction import BaseExtraction
from multiauth.lib.injection import BaseInjection
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters
from multiauth.lib.store.user import Credentials, User

PresetType = Literal['jwt_access_token_refresh_token', 'oauth_userpass', 'oauth_client_credentials', 'oauth_refresh']


##### Authentications ######


class RefreshPreset(BaseModel):
    request: HTTPRequestParameters
    extract: BaseExtraction
    inject: BaseInjection


##### Credentials ####


class UserPreset(Credentials):
    name: UserName = Field(description='The arbitrary name given to the user.')

    def to_credentials(self) -> Credentials:
        return Credentials(
            username=self.username,
            password=self.password,
            headers=self.headers,
            cookies=self.cookies,
            query_parameters=self.query_parameters,
            body=self.body,
        )


class BasePreset(BaseModel, abc.ABC):
    type: PresetType = Field(description='The type of the preset.')
    name: ProcedureName = Field(description='The name of the preset. Will be the name of the generated procedure.')

    request: HTTPRequestParameters | None = Field(
        default=None,
        description='The request parameters that define the authentication process.',
    )
    extract: BaseExtraction | None = Field(
        default=None,
        description='The way the token is going to be extracted from the authentication response.',
    )
    inject: BaseInjection | None = Field(
        default=None,
        description='The way the extracted token is going to be injected and formatted in the authenticated requests.',
    )
    refresh: RefreshPreset | None = Field(default=None, description='The definition of the refresh procedure.')

    users: Sequence[UserPreset] = Field(
        default=[],
        description='The list of users and their credentials that will use this authentication preset.',
    )

    @abc.abstractmethod
    def to_procedure_configuration(self) -> ProcedureConfiguration:
        ...

    @abc.abstractmethod
    def to_users(self) -> list[User]:
        ...
