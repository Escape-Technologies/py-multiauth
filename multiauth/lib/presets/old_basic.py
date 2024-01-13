from pydantic import Field

from multiauth.lib.presets.base_old import AuthPreset, UserPreset


class BasicUserPreset(UserPreset):
    username: str = Field(description='The Basic username of the user.')
    password: str = Field(description='The Basic password of the user.')


class BasicAuthPreset(AuthPreset):
    pass
