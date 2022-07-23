"""Multiauth types related to HTTP protocol."""

from enum import Enum, unique
from typing import Literal

HTTPMethod = Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT']


@unique
class Location(str, Enum):

    """The location where the auth data is added to."""
    HEADERS = 'headers'
    URL = 'url'
