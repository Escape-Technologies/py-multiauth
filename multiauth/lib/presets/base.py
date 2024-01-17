import abc
from typing import Literal, Sequence

from pydantic import Field

from multiauth.helpers.base_model import StrictBaseModel
from multiauth.helpers.slug import generate_seeded_slug
from multiauth.lib.entities import ProcedureName, UserName
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.store.user import User

PresetType = Literal[
    'basic',
    'cognito_userpass',
    'curl',
    'digest',
    'graphql',
    'headers',
    'http',
    'oauth_client_credentials',
    'oauth_userpass',
    'webdriver',
]


##### Credentials ####


class BaseUserPreset(StrictBaseModel, abc.ABC):
    username: UserName = Field(description='The username of the user.')


class BasePreset(StrictBaseModel, abc.ABC):
    type: PresetType = Field(description='The type of the preset.')

    users: Sequence[BaseUserPreset] = Field(
        description='A list of users to create',
    )

    @property
    def slug(self) -> ProcedureName:
        return ProcedureName(generate_seeded_slug(self.type + ''.join([user.username for user in self.users])))

    @abc.abstractmethod
    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        ...

    @abc.abstractmethod
    def to_users(self) -> list[User]:
        ...
