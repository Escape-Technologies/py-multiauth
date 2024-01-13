from pydantic import Field

from multiauth.lib.presets.base import BaseInjection, BasePreset, UserPreset


class APIKeyUserPreset(UserPreset):
    apiKey: str = Field(description='The API key of the user.')


class APIKeyInjectPreset(BaseInjection):
    key: str = Field(
        default='x-api-key',
        description='The name of parameter (header or cookie) containing the API key.',
    )


class APIKeyBasePreset(BasePreset):
    inject: APIKeyInjectPreset
