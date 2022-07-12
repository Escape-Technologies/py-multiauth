"""Graphql provider."""

from typing import Literal, TypedDict

from multiauth.types.http import HTTPMethod

Operation = Literal['query', 'mutation', 'subscription']


class AuthConfigGraphQl(TypedDict):

    """Authentication Configuration Parameters of the GraphQL Method."""
    url: str
    mutation_name: str
    cookie_auth: bool
    method: HTTPMethod
    mutation_field: str
    operation: Operation
    refresh_mutation_name: str | None
    refresh_field_name: str | None
    refresh_field: bool
    header_name: str | None
    header_key: str | None
    headers: dict[str, str] | None
