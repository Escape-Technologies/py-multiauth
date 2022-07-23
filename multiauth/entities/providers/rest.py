"""Rest provider."""

from typing import Dict, Optional, TypedDict

from multiauth.entities.http import HTTPMethod


class AuthConfigRest(TypedDict):

    """Authentication Configuration Parameters of the Rest Method."""
    url: str
    method: HTTPMethod
    cookie_auth: bool
    refresh_url: Optional[str]
    refresh_token_name: Optional[str]
    token_name: Optional[str]
    header_name: Optional[str]
    header_key: Optional[str]
    headers: Optional[Dict[str, str]]
