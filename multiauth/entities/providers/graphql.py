"""Graphql provider."""

import sys
from typing import Dict, Literal, Optional, TypeAlias

from multiauth.entities.http import HTTPMethod

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

Operation: TypeAlias = Literal['query', 'mutation', 'subscription']


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
