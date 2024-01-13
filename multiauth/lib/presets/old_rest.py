from typing import Any

from pydantic import Field

from multiauth.lib.presets.base import (
    BaseExtraction,
    BaseInjection,
    BasePreset,
    HTTPRequestParameters,
    RefreshPreset,
    UserPreset,
)


class RESTUserPreset(UserPreset):
    body: Any | None


class RESTRequestPreset(HTTPRequestParameters):
    pass


class RESTInjectPreset(BaseInjection):
    pass


class RESTExtractPreset(BaseExtraction):
    pass


class RESTBasePreset(BasePreset):
    request: RESTRequestPreset
    inject: RESTInjectPreset
    extract: RESTExtractPreset
    refresher: RefreshPreset | None = Field(default=None)
