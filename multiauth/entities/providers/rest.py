"""Rest provider."""

from enum import Enum

from pydantic import BaseModel

from multiauth.entities.http import HTTPMethod
from multiauth.entities.providers.http import HTTPLocation


class CredentialsEncoding(Enum):
    JSON = 'json'
    FORM = 'www-form-urlencoded'


class AuthConfigRest(BaseModel):

    """Authentication Configuration Parameters of the Rest Method."""

    url: str
    method: HTTPMethod
    refresh_url: str | None
    refresh_token_name: str | None
    token_name: str | None
    param_name: str | None
    param_prefix: str | None
    param_location: HTTPLocation
    headers: dict[str, str] | None
    credentials_encoding: CredentialsEncoding
