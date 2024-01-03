import abc
from typing import Literal

from pydantic import BaseModel, Field

from multiauth.entities.user import ProcedureName
from multiauth.revamp.lib.procedure import ProcedureConfiguration

PresetType = Literal['jwt_access_token_refresh_token', 'oauth_userpass']


class BasePreset(BaseModel, abc.ABC):
    type: PresetType = Field(description='The type of the preset.')
    name: ProcedureName = Field(description='The name of the preset. Will be the name of the generated procedure.')

    @abc.abstractmethod
    def to_procedure_configuration(self) -> ProcedureConfiguration:
        ...
