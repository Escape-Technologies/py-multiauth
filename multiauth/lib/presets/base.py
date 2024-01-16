import abc
import hashlib
import random
import string
from typing import Literal, Sequence

from pydantic import BaseModel, Field

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
]


##### Credentials ####


class BaseUserPreset(BaseModel, abc.ABC):
    username: UserName = Field(description='The username of the user.')


class BasePreset(BaseModel, abc.ABC):
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


def generate_seeded_slug(input_string: str, slug_length: int = 10) -> str:
    # Hash the input string
    hasher = hashlib.sha256()
    hasher.update(input_string.encode('utf-8'))
    hash_digest = hasher.digest()

    # Seed the random number generator
    seed = int.from_bytes(hash_digest, 'big')
    random.seed(seed)

    # Generate the slug
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(slug_length))
