"""Custom types of authentication module."""

from typing import (
    TypedDict,
)

from multiauth.entities.http import HTTPLocation


class AuthConfigApiKey(TypedDict):

    """Authentication Configuration Parameters of the Api Key Method."""

    param_location: HTTPLocation
    param_name: str
    param_prefix: str | None
    headers: dict[str, str] | None
