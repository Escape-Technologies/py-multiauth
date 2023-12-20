"""Graphql provider."""

from typing import Dict, Literal, Optional, TypedDict

from multiauth.entities.http import HTTPMethod
from multiauth.entities.providers.http import HTTPLocation

Operation = Literal['query', 'mutation', 'subscription']


class AuthConfigGraphQL(TypedDict):

    """Authentication Configuration Parameters of the GraphQL Method."""

    url: str
    mutation_name: str
    token_name: str
    method: HTTPMethod
    mutation_field: str
    operation: Operation
    refresh_mutation_name: Optional[str]
    refresh_field_name: Optional[str]
    refresh_field: bool
    param_name: Optional[str]
    param_prefix: Optional[str]
    param_location: HTTPLocation
    headers: Optional[Dict[str, str]]
