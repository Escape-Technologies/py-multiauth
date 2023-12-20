"""Custom data used in utils."""

from typing import NamedTuple

from multiauth.entities.http import HTTPMethod


class Credentials(NamedTuple):

    """This is the credentials class that are the credentials found in the curl."""

    username: str
    password: str


class ParsedCurlContent(NamedTuple):

    """This is the datatype which shows the curl command."""

    method: HTTPMethod
    url: str
    data: str | None
    headers: dict[str, str]
    credentials: Credentials | None
