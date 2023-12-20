"""Rest provider."""

from enum import Enum
from typing import (
    Optional,
    TypedDict,
)

from multiauth.entities.http import HTTPMethod
from multiauth.entities.providers.http import HTTPLocation


class CredentialsEncoding(Enum):
    JSON = 'json'
    FORM = 'www-form-urlencoded'


class AuthConfigRest(TypedDict):

    """Authentication Configuration Parameters of the Rest Method."""

    url: str
    method: HTTPMethod
    refresh_url: Optional[str]
    refresh_token_name: Optional[str]
    token_name: Optional[str]
    param_name: Optional[str]
    param_prefix: Optional[str]
    param_location: HTTPLocation
    headers: Optional[dict[str, str]]
    credentials_encoding: CredentialsEncoding
