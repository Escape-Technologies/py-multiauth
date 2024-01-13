from pydantic import BaseModel, Field

from multiauth.lib.extraction import BaseExtraction
from multiauth.lib.injection import BaseInjection
from multiauth.lib.runners.http import HTTPRequestParameters
from multiauth.lib.store.user import Credentials, UserName

##### Authentications ######

RequestPreset = HTTPRequestParameters
ExtractPreset = BaseExtraction
InjectPreset = BaseInjection


class RefreshPreset(BaseModel):
    request: RequestPreset
    extract: ExtractPreset
    inject: InjectPreset


##### Credentials ####


class UserPreset(Credentials):
    name: UserName = Field(description='The arbitrary name given to the user.')


class AuthPreset(BaseModel):
    request: RequestPreset | None = Field(default=None)
    extract: ExtractPreset | None = Field(default=None)
    inject: InjectPreset | None = Field(default=None)
    refresh: RefreshPreset | None = Field(default=None)
    users: list[UserPreset]
