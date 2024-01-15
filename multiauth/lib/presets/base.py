import abc
from typing import Literal, Sequence

from pydantic import BaseModel, Field

from multiauth.lib.entities import ProcedureName, UserName
from multiauth.lib.extraction import BaseExtraction  # noqa: F401
from multiauth.lib.injection import BaseInjection  # noqa: F401
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters  # noqa: F401
from multiauth.lib.store.user import Credentials, User

PresetType = Literal[
    'jwt_access_token_refresh_token',
    'oauth_userpass',
    'oauth_client_credentials',
    'oauth_refresh',
    'basic',
    'graphql',
]


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
    name: ProcedureName = Field(description='The arbitrary name given to the preset.')

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
