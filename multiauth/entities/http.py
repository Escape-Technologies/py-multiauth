"""Multiauth types related to HTTP protocol."""

import sys
from dataclasses import dataclass, field
from enum import Enum, StrEnum, unique

if sys.version_info >= (3, 8):
    from typing import Literal  # pylint: disable=no-name-in-module
else:
    from typing_extensions import Literal

HTTPMethod = Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT']


@unique
class Location(str, Enum):

    """The location where the auth data is added to."""

    HEADERS = 'headers'
    URL = 'url'

class HttpScheme(StrEnum):
    HTTP = 'http'
    HTTPS = 'https'

JSONSerializable = dict | list | str | int | float | bool | None

@dataclass
class HttpRequest:
    method: HTTPMethod
    host: str
    scheme: HttpScheme
    path: str = '/'
    headers: dict[str, str] = field(default_factory=dict)
    username: str | None = None
    password: str | None = None
    json: JSONSerializable | None = None
    data: str | None = None
    query_parameters: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    timeout: int = 5
