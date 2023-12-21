"""Graphql provider."""

from typing import Literal

from pydantic import BaseModel

from multiauth.entities.http import HTTPMethod
from multiauth.entities.providers.http import HTTPLocation

Operation = Literal['query', 'mutation', 'subscription']


class AuthConfigGraphQL(BaseModel):

    """Authentication Configuration Parameters of the GraphQL Method."""

    url: str
    mutation_name: str
    token_name: str
    method: HTTPMethod
    mutation_field: str
    operation: Operation
    refresh_mutation_name: str | None
    refresh_field_name: str | None
    refresh_field: bool
    param_name: str | None
    param_prefix: str | None
    param_location: HTTPLocation
    headers: dict[str, str] | None
