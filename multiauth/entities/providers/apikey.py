"""Custom types of authentication module."""


from pydantic import BaseModel

from multiauth.entities.http import HTTPLocation


class AuthConfigApiKey(BaseModel):

    """Authentication Configuration Parameters of the Api Key Method."""

    param_location: HTTPLocation
    param_name: str
    param_prefix: str | None
    headers: dict[str, str] | None
