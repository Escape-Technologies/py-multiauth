from pydantic import Field

from multiauth.lib.presets.base import BasePreset, UserPreset


class BasicUserPreset(UserPreset):
    username: str = Field(description='The Basic username of the user.')
    password: str = Field(description='The Basic password of the user.')


class BasicBasePreset(BasePreset):
    pass
