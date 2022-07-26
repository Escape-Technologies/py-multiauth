"""Graphql provider."""

from typing import Dict, Literal, Optional, TypedDict

from multiauth.entities.http import HTTPMethod

Operation = Literal['query', 'mutation', 'subscription']


class AuthConfigGraphQl(TypedDict):

    """Authentication Configuration Parameters of the GraphQL Method."""
    url: str
    mutation_name: str
    cookie_auth: bool
    method: HTTPMethod
    mutation_field: str
    operation: Operation
    refresh_mutation_name: Optional[str]
    refresh_field_name: Optional[str]
    refresh_field: bool
    header_name: Optional[str]
    header_key: Optional[str]
    headers: Optional[Dict[str, str]]
