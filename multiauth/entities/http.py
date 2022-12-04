"""Multiauth types related to HTTP protocol."""

from enum import Enum, unique


@unique
class Location(str, Enum):

    """The location where the auth data is added to."""
    HEADERS = 'headers'
    URL = 'url'
