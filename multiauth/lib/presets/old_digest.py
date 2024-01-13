from multiauth.lib.presets.base_old import UserPreset


class DigestUserPreset(UserPreset):
    username: str
    password: str
