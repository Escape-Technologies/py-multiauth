from pydantic import BaseModel, Field

from multiauth.revamp.lib.http_core.entities import HTTPLocation


class TokenInjection(BaseModel):
    location: HTTPLocation
    key: str
    prefix: str | None = Field(default=None)
    variable: str | None = Field(default=None)
