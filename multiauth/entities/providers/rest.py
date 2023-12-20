"""Rest provider."""

import sys
from enum import Enum
from typing import Dict, Optional

from multiauth.entities.http import HTTPMethod
from multiauth.entities.providers.http import HTTPLocation

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


class CredentialsEncoding(Enum):
    JSON = 'json'
    FORM = 'www-form-urlencoded'


class AuthConfigRest(TypedDict):

    """Authentication Configuration Parameters of the Rest Method."""

    url: str
    method: HTTPMethod
    location: HTTPLocation
    refresh_url: Optional[str]
    refresh_token_name: Optional[str]
    token_name: Optional[str]
    param_name: Optional[str]
    param_prefix: Optional[str]
    headers: Optional[Dict[str, str]]
    credentials_encoding: CredentialsEncoding
