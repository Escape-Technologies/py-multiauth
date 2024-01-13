from pydantic import Field

from multiauth.lib.presets.base_old import AuthPreset, InjectPreset, UserPreset


class APIKeyUserPreset(UserPreset):
    apiKey: str = Field(description='The API key of the user.')


class APIKeyInjectPreset(InjectPreset):
    key: str = Field(
        default='x-api-key',
        description='The name of parameter (header or cookie) containing the API key.',
    )


class APIKeyAuthPreset(AuthPreset):
    inject: APIKeyInjectPreset
