"""Rest provider."""

import sys
from typing import Dict, Optional

from multiauth.entities.http import HTTPMethod

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict


class AuthConfigRest(TypedDict):

    """Authentication Configuration Parameters of the Rest Method."""

    url: str
    method: HTTPMethod
    cookie_auth: bool
    refresh_url: Optional[str]
    refresh_token_name: Optional[str]
    token_name: Optional[str]
    header_name: Optional[str]
    header_prefix: Optional[str]
    headers: Optional[Dict[str, str]]
