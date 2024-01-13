from typing import Any

from pydantic import Field

from multiauth.lib.presets.base_old import (
    AuthPreset,
    ExtractPreset,
    InjectPreset,
    RefreshPreset,
    RequestPreset,
    UserPreset,
)


class RESTUserPreset(UserPreset):
    body: Any | None


class RESTRequestPreset(RequestPreset):
    pass


class RESTInjectPreset(InjectPreset):
    pass


class RESTExtractPreset(ExtractPreset):
    pass


class RESTAuthPreset(AuthPreset):
    request: RESTRequestPreset
    inject: RESTInjectPreset
    extract: RESTExtractPreset
    refresher: RefreshPreset | None = Field(default=None)
