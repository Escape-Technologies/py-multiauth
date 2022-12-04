"""Custom data used in utils."""

from http import HTTPMethod
from typing import Dict, NamedTuple, Optional


class Credentials(NamedTuple):

    """This is the credentials class that are the credentials found in the curl."""
    username: str
    password: str


class ParsedCurlContent(NamedTuple):

    """This is the datatype which shows the curl command."""

    method: HTTPMethod
    url: str
    data: Optional[str]
    headers: Dict[str, str]
    credentials: Optional[Credentials]
