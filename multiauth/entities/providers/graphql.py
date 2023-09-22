"""Graphql provider."""

import sys
from typing import Dict, Optional

from multiauth.entities.http import HTTPMethod

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import Literal, TypedDict

Operation = Literal['query', 'mutation', 'subscription']


class AuthConfigGraphQL(TypedDict):

    """Authentication Configuration Parameters of the GraphQL Method."""

    url: str
    mutation_name: str
    cookie_auth: bool
    method: HTTPMethod
    mutation_field: str
    operation: Operation
    header_token_name: Optional[str]
    refresh_mutation_name: Optional[str]
    refresh_field_name: Optional[str]
    refresh_field: bool
    header_name: Optional[str]
    header_prefix: Optional[str]
    headers: Optional[Dict[str, str]]
