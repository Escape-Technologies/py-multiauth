"""Multiauth types related to HTTP protocol."""

import sys

if sys.version_info >= (3, 8):
    from typing import Literal  # pylint: disable=no-name-in-module
else:
    from typing_extensions import Literal

HTTPMethod = Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT']
