import abc
from typing import Literal, Sequence

from pydantic import Field
from pydantic.annotated_handlers import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

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


class BasePresetDoc(StrictBaseModel):
    kind: Literal['preset'] = Field(default='preset', description='The kind of the preset.')
    title: str = Field(description='The title of the preset for the Documentation.')
    description: str = Field(description='The markdown description of the preset for the Documentation')
    examples: list = Field(description='A list of examples of the preset for the Documentation')


##### Credentials ####


class BaseUserPreset(StrictBaseModel, abc.ABC):
    username: UserName = Field(description='The username of the user.')
    headers: dict[str, str] | None = Field(
        default=None,
        description='Optional headers injected during the authentication process and in authentified requests.',
    )
    cookies: dict[str, str] | None = Field(
        default=None,
        description='Optional cookies injected during the authentication process and in authentified requests.',
    )


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

    @staticmethod
    @abc.abstractmethod
    def _doc() -> BasePresetDoc:
        ...

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        __core_schema: CoreSchema,
        __handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        json_schema = __handler(__core_schema)
        json_schema = __handler.resolve_ref_schema(json_schema)
        json_schema['_doc'] = cls._doc().model_dump(exclude_none=True)
        return json_schema
