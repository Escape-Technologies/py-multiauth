"""Multiauth types related to HTTP protocol."""


from typing import Literal

HTTPMethod = Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT']
