"""Rest provider."""

from typing import TypedDict

from multiauth.types.http import HTTPMethod


class AuthConfigRest(TypedDict):

    """Authentication Configuration Parameters of the Rest Method."""
    url: str
    method: HTTPMethod
    cookie_auth: bool
    refresh_url: str | None
    refresh_token_name: str | None
    token_name: str | None
    header_name: str | None
    header_key: str | None
    headers: dict[str, str] | None
