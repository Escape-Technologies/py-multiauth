from multiauth.lib.presets.base import UserPreset


class DigestUserPreset(UserPreset):
    username: str
    password: str
